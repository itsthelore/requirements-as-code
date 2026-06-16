"""Tests for prompt-complexity routing (`rac route`, ADR-068).

Covers the pure scorer, the config loader, the service, and the CLI. The
through-line is the boundary: RAC produces a deterministic structural score and a
local/cloud recommendation, and never anything that requires a model.
"""

from __future__ import annotations

import io
import json

import pytest

from rac import ComplexityScore, RoutingConfig, route_text, score_complexity
from rac.cli import main
from rac.core.complexity import (
    DEFAULT_THRESHOLD,
    FEATURE_ORDER,
    extract_features,
)
from rac.services.init import MalformedRepositoryConfig, load_routing_config
from rac.services.route import route_file

TRIVIAL = "Say hello."

COMPLEX = """# Build the reporting pipeline

## Context

We need a deterministic batch pipeline that ingests events and emits a daily
report, with retries and backfill, across three environments.

## Steps

- Parse the input manifest
- Validate every row against the schema
- Deduplicate by event id
- Aggregate per day
- Render the report
- Upload the artifact
- Notify the channel

## Reference

See [the spec](https://example.com/spec) and [the schema](https://example.com/schema).

## Example

```python
def pipeline(rows):
    return aggregate(dedupe(validate(rows)))
```

| Field | Type |
| --- | --- |
| id | string |
| ts | int |
"""

BODY = "# Task\n\nDo the thing.\n\n## Steps\n\n- one\n- two\n"
WITH_FRONTMATTER = "---\nschema_version: 1\nid: RAC-TESTROUTE01\ntype: prompt\n---\n" + BODY


# --- core scorer ------------------------------------------------------------


def test_score_is_deterministic_and_bounded():
    a = score_complexity(COMPLEX)
    b = score_complexity(COMPLEX)
    assert a.to_dict() == b.to_dict()
    assert 0.0 <= a.score <= 1.0


def test_complex_prompt_scores_higher_than_trivial():
    assert score_complexity(COMPLEX).score > score_complexity(TRIVIAL).score


def test_trivial_prompt_routes_local_by_default():
    result = score_complexity(TRIVIAL)
    assert result.recommendation == "local"
    assert result.threshold == DEFAULT_THRESHOLD


def test_features_cover_the_declared_order():
    assert set(score_complexity(COMPLEX).features) == set(FEATURE_ORDER)


def test_frontmatter_is_stripped_so_artifact_equals_its_body():
    # The stored-artifact <-> stdin-text equivalence: scoring a Prompt artifact
    # scores its prompt, not the YAML envelope.
    assert extract_features(WITH_FRONTMATTER) == extract_features(BODY)


def test_code_fence_contents_are_not_counted_as_structure():
    features = extract_features("```\n## Not a heading\n- not a list\n| a | b |\n```\n")
    assert features["heading_count"] == 0
    assert features["list_item_count"] == 0
    assert features["table_row_count"] == 0
    assert features["code_block_count"] == 1


def test_recommendation_flips_at_the_threshold():
    score = score_complexity(COMPLEX).score
    assert score > 0.0
    # At exactly the threshold the recommendation is cloud (score >= threshold).
    at = score_complexity(COMPLEX, config=RoutingConfig(threshold=score))
    assert at.recommendation == "cloud"
    above = score_complexity(COMPLEX, config=RoutingConfig(threshold=min(1.0, score + 0.01)))
    assert above.recommendation == "local"


def test_score_and_recommendation_are_consistent():
    for text in (TRIVIAL, COMPLEX):
        result = score_complexity(text)
        expected = "cloud" if result.score >= result.threshold else "local"
        assert result.recommendation == expected


# --- config loader ----------------------------------------------------------


def _write_config(tmp_path, routing_body: str) -> str:
    config_dir = tmp_path / ".rac"
    config_dir.mkdir()
    config = "repository_key: RAC\n" + routing_body
    (config_dir / "config.yaml").write_text(config, encoding="utf-8")
    return str(tmp_path)


def test_no_config_yields_defaults(tmp_path):
    config = load_routing_config(str(tmp_path))
    assert config.threshold == DEFAULT_THRESHOLD
    assert config == RoutingConfig()


def test_config_overrides_threshold(tmp_path):
    start = _write_config(tmp_path, "routing:\n  threshold: 0.8\n")
    assert load_routing_config(start).threshold == 0.8


def test_config_merges_weights_over_defaults(tmp_path):
    start = _write_config(tmp_path, "routing:\n  weights:\n    word_count: 9\n")
    config = load_routing_config(start)
    assert config.weights["word_count"] == 9.0
    # Unspecified weights keep their defaults.
    assert config.weights["heading_count"] == RoutingConfig().weights["heading_count"]


@pytest.mark.parametrize(
    "routing_body",
    [
        "routing:\n  threshold: 2.0\n",  # out of range
        "routing:\n  threshold: high\n",  # not a number
        "routing: not-a-mapping\n",  # wrong shape
        "routing:\n  weights:\n    bogus_feature: 1\n",  # unknown feature
        "routing:\n  weights:\n    word_count: -1\n",  # negative weight
    ],
)
def test_malformed_routing_config_is_rejected(tmp_path, routing_body):
    start = _write_config(tmp_path, routing_body)
    with pytest.raises(MalformedRepositoryConfig):
        load_routing_config(start)


# --- service ----------------------------------------------------------------


def test_route_text_uses_configured_threshold(tmp_path):
    start = _write_config(tmp_path, "routing:\n  threshold: 0.0\n")
    # A zero threshold routes even a trivial prompt (score 0.0 >= 0.0) to cloud.
    assert route_text(TRIVIAL, start_dir=start).recommendation == "cloud"


def test_threshold_argument_overrides_config(tmp_path):
    start = _write_config(tmp_path, "routing:\n  threshold: 0.0\n")
    assert route_text(TRIVIAL, start_dir=start, threshold=0.99).recommendation == "local"


def test_route_file_reads_and_strips_frontmatter(tmp_path):
    artifact = tmp_path / "prompt.md"
    artifact.write_text(WITH_FRONTMATTER, encoding="utf-8")
    result = route_file(str(artifact))
    assert isinstance(result, ComplexityScore)
    assert result.features == extract_features(BODY)


# --- CLI --------------------------------------------------------------------


def _feed_stdin(monkeypatch, text: str) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(text))


def test_cli_route_stdin_human(monkeypatch, capsys):
    _feed_stdin(monkeypatch, TRIVIAL)
    rc = main(["route", "-"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Recommended Model:" in out
    assert "LOCAL" in out


def test_cli_route_json_is_versioned_contract(monkeypatch, capsys):
    _feed_stdin(monkeypatch, COMPLEX)
    rc = main(["route", "-", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["schema_version"] == "1"
    assert payload["recommendation"] in ("local", "cloud")
    assert set(payload["features"]) == set(FEATURE_ORDER)
    assert 0.0 <= payload["score"] <= 1.0


def test_cli_route_is_deterministic(monkeypatch, capsys):
    _feed_stdin(monkeypatch, COMPLEX)
    main(["route", "-", "--json"])
    first = capsys.readouterr().out
    _feed_stdin(monkeypatch, COMPLEX)
    main(["route", "-", "--json"])
    second = capsys.readouterr().out
    assert first == second


def test_cli_route_file_not_found_is_usage_error(capsys):
    rc = main(["route", "does-not-exist.md"])
    assert rc == 2
    assert "file not found" in capsys.readouterr().err


def test_cli_route_threshold_out_of_range_is_usage_error(monkeypatch, capsys):
    _feed_stdin(monkeypatch, TRIVIAL)
    rc = main(["route", "-", "--threshold", "5"])
    assert rc == 2
    assert "--threshold" in capsys.readouterr().err


def test_cli_route_malformed_config_is_failure(tmp_path, monkeypatch, capsys):
    _write_config(tmp_path, "routing:\n  threshold: 2.0\n")
    monkeypatch.chdir(tmp_path)
    _feed_stdin(monkeypatch, TRIVIAL)
    rc = main(["route", "-"])
    assert rc == 1
    assert "routing.threshold" in capsys.readouterr().err
