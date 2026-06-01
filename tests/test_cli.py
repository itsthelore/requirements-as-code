"""Tests for the CLI: exit codes and JSON output."""

from __future__ import annotations

import json

import pytest

from rac.cli import main

from conftest import fixture_path


def test_validate_valid_exits_zero(capsys):
    rc = main(["validate", fixture_path("valid", "feature.md")])
    assert rc == 0
    assert "PASS" in capsys.readouterr().out


def test_validate_invalid_exits_one(capsys):
    rc = main(["validate", fixture_path("invalid", "duplicate_ids.md")])
    assert rc == 1
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "duplicate-req-id" in out


def test_validate_missing_file_exits_two():
    with pytest.raises(SystemExit) as exc:
        main(["validate", fixture_path("valid", "does_not_exist.md")])
    assert exc.value.code == 2


def test_validate_json_shape(capsys):
    rc = main(["validate", fixture_path("invalid", "malformed_id.md"), "--json"])
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is False
    assert {"file", "valid", "errors", "warnings"} <= payload.keys()
    assert any(e["code"] == "malformed-req-id" for e in payload["errors"])


def test_diff_exits_zero_and_reports(capsys):
    rc = main(["diff", fixture_path("diff", "old.md"), fixture_path("diff", "new.md")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Added Requirements" in out
    assert "REQ-004" in out
    assert "Before:" in out and "After:" in out  # modified-requirement format


def test_diff_json_shape(capsys):
    rc = main(
        [
            "diff",
            fixture_path("diff", "old.md"),
            fixture_path("diff", "new.md"),
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert [r["id"] for r in payload["added_requirements"]] == ["REQ-004"]
    assert [r["id"] for r in payload["removed_requirements"]] == ["REQ-003"]
    assert [c["id"] for c in payload["modified_requirements"]] == ["REQ-002"]
