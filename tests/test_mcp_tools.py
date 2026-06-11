"""Guide tool contracts — output shapes, truncation, errors (v0.10.0).

The golden practice applied to the MCP surface: every tool's output shape is
pinned against fixture corpora, truncation is pinned at whole-item boundaries,
and the structured error shapes are pinned to the resolver's own (ADR-007,
ADR-032, ADR-033). Equivalence tests prove the tool payloads are the same
objects the CLI's JSON output serializes — no second source of truth. A
freshness test edits the corpus between calls and observes the change, pinning
the stateless re-read contract (ADR-032).
"""

from __future__ import annotations

import asyncio
import json

import pytest
from conftest import fixture_path

from rac.mcp.budget import (
    DEFAULT_BUDGET,
    HINT_CONTENT,
    HINT_RELATED,
    HINT_SEARCH,
    serialize,
)
from rac.mcp.server import build_server
from rac.output import json as json_output
from rac.services.portfolio import build_portfolio_summary
from rac.services.resolve import find_artifacts, resolve_artifact

CORPUS = fixture_path("mcp", "corpus")
DUPLICATE = fixture_path("mcp", "duplicate")

DEC = "RAC-MCPDEC000001"
REQ = "RAC-MCPREQ000001"
RDM = "RAC-MCPRDM000001"
DUP = "RAC-MCPDP0000001"


def call(root: str, tool: str, args: dict, budget: int = DEFAULT_BUDGET) -> dict:
    """Invoke a tool against ``root`` and parse its single JSON text result."""
    server = build_server(root, budget=budget)
    contents, _structured = asyncio.run(server.call_tool(tool, args))
    assert len(contents) == 1
    return json.loads(contents[0].text)


# --- get_artifact ------------------------------------------------------------


def test_get_artifact_resolved_shape():
    payload = call(CORPUS, "get_artifact", {"id": DEC})
    assert list(payload) == ["schema_version", "id", "type", "title", "path", "content"]
    assert payload["schema_version"] == "1"
    assert payload["id"] == DEC
    assert payload["type"] == "decision"
    assert payload["title"] == "Use an Event Bus"
    # content is the file text exactly as stored, frontmatter included.
    with open(payload["path"], encoding="utf-8") as fh:
        assert payload["content"] == fh.read()
    assert payload["content"].startswith("---\nschema_version: 1\n")
    assert "truncated" not in payload


def test_get_artifact_metadata_matches_cli_resolve_json():
    payload = call(CORPUS, "get_artifact", {"id": DEC})
    cli = json.loads(json_output.render_resolve_json(resolve_artifact(CORPUS, DEC)))
    # The resolver's answer (everything but the server-added content) is the
    # same object the CLI serializes.
    assert {k: payload[k] for k in cli} == cli


def test_get_artifact_not_found_error_shape():
    payload = call(CORPUS, "get_artifact", {"id": "RAC-MCPZZZ000099"})
    assert payload == {
        "schema_version": "1",
        "error": "not-found",
        "id": "RAC-MCPZZZ000099",
    }


def test_get_artifact_duplicate_error_shape():
    payload = call(DUPLICATE, "get_artifact", {"id": DUP})
    assert payload["schema_version"] == "1"
    assert payload["error"] == "duplicate"
    assert payload["id"] == DUP
    assert payload["paths"] == sorted(payload["paths"])
    assert len(payload["paths"]) == 2


def test_get_artifact_error_matches_cli_resolve_json():
    payload = call(DUPLICATE, "get_artifact", {"id": DUP})
    cli = json.loads(json_output.render_resolve_json(resolve_artifact(DUPLICATE, DUP)))
    assert payload == cli


# --- search_artifacts --------------------------------------------------------


def test_search_artifacts_shape_and_order():
    payload = call(CORPUS, "search_artifacts", {"query": "RAC-MCP"})
    assert list(payload) == ["schema_version", "query", "type", "match_count", "matches"]
    assert payload["query"] == "RAC-MCP"
    assert payload["type"] is None
    assert payload["match_count"] == 3
    for match in payload["matches"]:
        assert list(match) == ["id", "type", "title", "path"]
    assert "truncated" not in payload


def test_search_artifacts_type_filter():
    payload = call(CORPUS, "search_artifacts", {"query": "RAC-MCP", "type": "decision"})
    assert payload["type"] == "decision"
    assert [m["id"] for m in payload["matches"]] == [DEC]


def test_search_artifacts_matches_cli_find_json():
    payload = call(CORPUS, "search_artifacts", {"query": "messaging"})
    cli = json.loads(json_output.render_find_json(find_artifacts(CORPUS, "messaging")))
    assert payload == cli


def test_search_artifacts_empty_result_is_not_an_error():
    payload = call(CORPUS, "search_artifacts", {"query": "no-such-token"})
    assert payload["match_count"] == 0
    assert payload["matches"] == []
    assert "error" not in payload


# --- get_related -------------------------------------------------------------


def test_get_related_outgoing_and_incoming_shape():
    payload = call(CORPUS, "get_related", {"id": DEC})
    assert list(payload) == [
        "schema_version",
        "id",
        "type",
        "title",
        "path",
        "outgoing",
        "incoming",
    ]
    # outgoing: the artifact's own sections, snake_case, references as stored.
    assert payload["outgoing"] == {"related_requirements": [REQ]}
    # incoming: artifacts whose references resolve here, ordered by path/section.
    assert payload["incoming"] == [
        {
            "id": REQ,
            "type": "requirement",
            "title": "Decoupled Messaging",
            "path": fixture_path("mcp", "corpus", "requirement.md"),
            "section": "related_decisions",
        },
        {
            "id": RDM,
            "type": "roadmap",
            "title": "Messaging Roadmap",
            "path": fixture_path("mcp", "corpus", "roadmap.md"),
            "section": "related_decisions",
        },
    ]


def test_get_related_incoming_ordered_by_path_then_section():
    payload = call(CORPUS, "get_related", {"id": DEC})
    keys = [(e["path"], e["section"]) for e in payload["incoming"]]
    assert keys == sorted(keys)


def test_get_related_no_incoming_yields_empty_list():
    # The requirement is referenced by the decision and the roadmap, but a leaf
    # with no inbound references must still produce a valid empty incoming list.
    payload = call(CORPUS, "get_related", {"id": RDM})
    assert payload["incoming"] == []
    assert "related_decisions" in payload["outgoing"]


def test_get_related_not_found_error_shape():
    payload = call(CORPUS, "get_related", {"id": "RAC-MCPZZZ000099"})
    assert payload == {
        "schema_version": "1",
        "error": "not-found",
        "id": "RAC-MCPZZZ000099",
    }


def test_get_related_duplicate_error_shape():
    payload = call(DUPLICATE, "get_related", {"id": DUP})
    assert payload["error"] == "duplicate"
    assert payload["id"] == DUP


# --- get_summary -------------------------------------------------------------


def test_get_summary_matches_portfolio_to_dict():
    payload = call(CORPUS, "get_summary", {})
    assert payload == build_portfolio_summary(CORPUS, recursive=True).to_dict()


def test_get_summary_matches_cli_portfolio_json():
    payload = call(CORPUS, "get_summary", {})
    cli = json.loads(json_output.render_portfolio_json(build_portfolio_summary(CORPUS)))
    assert payload == cli


# --- determinism -------------------------------------------------------------


@pytest.mark.parametrize(
    "tool,args",
    [
        ("get_artifact", {"id": DEC}),
        ("search_artifacts", {"query": "RAC-MCP"}),
        ("get_related", {"id": DEC}),
        ("get_summary", {}),
    ],
)
def test_tool_output_is_deterministic(tool, args):
    first = build_server(CORPUS)
    second = build_server(CORPUS)
    out1 = asyncio.run(first.call_tool(tool, args))[0][0].text
    out2 = asyncio.run(second.call_tool(tool, args))[0][0].text
    assert out1 == out2


# --- truncation (budget enforcement) -----------------------------------------


def test_search_truncates_whole_matches_with_marker():
    # A budget that fits the envelope plus some but not all three matches.
    full = call(CORPUS, "search_artifacts", {"query": "RAC-MCP"})
    assert full["match_count"] == 3 and "truncated" not in full

    budget = 250
    payload = call(CORPUS, "search_artifacts", {"query": "RAC-MCP"}, budget=budget)
    assert payload["truncated"] is True
    assert payload["hint"] == HINT_SEARCH
    # match_count reports the true total; matches is a whole-item prefix.
    assert payload["match_count"] == 3
    assert len(payload["matches"]) < 3
    assert payload["omitted"] == 3 - len(payload["matches"])
    # Every kept match is a complete entry (never mid-element).
    for match in payload["matches"]:
        assert set(match) == {"id", "type", "title", "path"}
    assert len(serialize(payload, budget)) <= budget or payload["matches"] == []


def test_related_truncates_whole_incoming_entries():
    budget = 300
    payload = call(CORPUS, "get_related", {"id": DEC}, budget=budget)
    assert payload["truncated"] is True
    assert payload["hint"] == HINT_RELATED
    assert payload["omitted"] == 2 - len(payload["incoming"])
    for entry in payload["incoming"]:
        assert set(entry) == {"id", "type", "title", "path", "section"}


def test_artifact_truncates_content_tail():
    budget = 250
    payload = call(CORPUS, "get_artifact", {"id": DEC}, budget=budget)
    assert payload["truncated"] is True
    assert payload["hint"] == HINT_CONTENT
    full = call(CORPUS, "get_artifact", {"id": DEC})
    # The kept content is a head prefix of the full content (tail dropped).
    assert full["content"].startswith(payload["content"])
    assert payload["omitted"] == len(full["content"]) - len(payload["content"])


def test_truncated_marker_absent_on_complete_responses():
    for tool, args in [
        ("get_artifact", {"id": DEC}),
        ("search_artifacts", {"query": "RAC-MCP"}),
        ("get_related", {"id": DEC}),
        ("get_summary", {}),
    ]:
        payload = call(CORPUS, tool, args)
        assert "truncated" not in payload
        assert "omitted" not in payload
        assert "hint" not in payload


def test_serialize_respects_budget_at_boundary():
    # Whole-item truncation keeps the serialized response within budget once a
    # boundary fits, and the kept prefix is deterministic.
    payload = {
        "schema_version": "1",
        "query": "x",
        "type": None,
        "match_count": 3,
        "matches": [
            {"id": f"RAC-AAAAAAAAAA0{n}", "type": "t", "title": "T", "path": "p"} for n in range(3)
        ],
    }
    serialized = serialize(payload, budget=160)
    reparsed = json.loads(serialized)
    assert reparsed["truncated"] is True
    assert len(reparsed["matches"]) < 3


# --- freshness (stateless re-read, ADR-032) ----------------------------------


def test_each_call_rereads_the_repository(tmp_path):
    artifact = tmp_path / "thing.md"
    artifact.write_text(
        "---\nschema_version: 1\nid: RAC-MCPFRESH0001\ntype: decision\n---\n"
        "# Original Title\n\n## Status\n\nAccepted\n\n## Category\n\nArchitecture\n\n"
        "## Context\n\nC.\n\n## Decision\n\nD.\n\n## Consequences\n\nE.\n",
        encoding="utf-8",
    )
    root = str(tmp_path)

    before = call(root, "get_artifact", {"id": "RAC-MCPFRESH0001"})
    assert before["title"] == "Original Title"

    # Edit the file between calls; a stateless server must observe the change.
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace("Original Title", "Edited Title"),
        encoding="utf-8",
    )

    after = call(root, "get_artifact", {"id": "RAC-MCPFRESH0001"})
    assert after["title"] == "Edited Title"
    assert "Edited Title" in after["content"]
