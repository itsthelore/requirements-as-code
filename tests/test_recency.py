"""Tests for git-derived artifact recency (v0.13.2, ADR-045).

Each test builds a throwaway git repository under ``tmp_path`` with controlled
commit times; the suite never touches this repository's own git state. Recency
is read-only and degrades to "unknown" (``None``) outside git or for
uncommitted files, never raising.
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

from rac.services.recency import artifact_recency

_REQUIREMENT = "# {title}\n\n## Problem\n\np\n\n## Requirements\n\n[REQ-001] x\n"
_DECISION = "# {title}\n\n## Context\n\nc\n\n## Decision\n\nd\n\n## Consequences\n\nk\n"


def _git(repo: Path, *args: str, when: str | None = None) -> None:
    env = dict(os.environ)
    if when is not None:
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        env=env,
    )


def _init(repo: Path) -> None:
    _git(repo, "init", "--quiet", "--initial-branch=main")


# --- service -----------------------------------------------------------------


def test_recency_returns_known_commit_time(tmp_path):
    _init(tmp_path)
    corpus = tmp_path / "rac" / "requirements"
    corpus.mkdir(parents=True)
    (corpus / "a.md").write_text(_REQUIREMENT.format(title="A"), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "--quiet", "-m", "init", when="2026-01-01T12:00:00+00:00")

    report = artifact_recency(str(tmp_path))
    assert len(report.artifacts) == 1
    art = report.artifacts[0]
    assert art.last_committed == datetime.fromisoformat("2026-01-01T12:00:00+00:00")
    assert report.most_recent == datetime.fromisoformat("2026-01-01T12:00:00+00:00")


def test_recency_unknown_for_uncommitted_file(tmp_path):
    _init(tmp_path)
    corpus = tmp_path / "rac" / "requirements"
    corpus.mkdir(parents=True)
    (corpus / "committed.md").write_text(_REQUIREMENT.format(title="C"), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "--quiet", "-m", "init", when="2026-01-01T12:00:00+00:00")
    # A new, never-committed artifact.
    (corpus / "new.md").write_text(_REQUIREMENT.format(title="N"), encoding="utf-8")

    report = artifact_recency(str(tmp_path))
    by_path = {Path(a.path).name: a.last_committed for a in report.artifacts}
    assert by_path["committed.md"] is not None
    assert by_path["new.md"] is None
    # Aggregate ignores the unknown.
    assert report.most_recent == datetime.fromisoformat("2026-01-01T12:00:00+00:00")


def test_recency_most_recent_by_type(tmp_path):
    _init(tmp_path)
    reqs = tmp_path / "rac" / "requirements"
    decs = tmp_path / "rac" / "decisions"
    reqs.mkdir(parents=True)
    decs.mkdir(parents=True)
    (reqs / "r.md").write_text(_REQUIREMENT.format(title="R"), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "--quiet", "-m", "req", when="2026-01-01T00:00:00+00:00")
    (decs / "d.md").write_text(_DECISION.format(title="D"), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "--quiet", "-m", "dec", when="2026-03-01T00:00:00+00:00")

    report = artifact_recency(str(tmp_path))
    by_type = report.most_recent_by_type()
    assert by_type["requirement"] == datetime.fromisoformat("2026-01-01T00:00:00+00:00")
    assert by_type["decision"] == datetime.fromisoformat("2026-03-01T00:00:00+00:00")
    # The overall aggregate is the newest of the two.
    assert report.most_recent == datetime.fromisoformat("2026-03-01T00:00:00+00:00")


def test_recency_outside_git_is_all_unknown(tmp_path):
    # No `git init`: a plain directory of artifacts.
    corpus = tmp_path / "rac" / "requirements"
    corpus.mkdir(parents=True)
    (corpus / "a.md").write_text(_REQUIREMENT.format(title="A"), encoding="utf-8")

    report = artifact_recency(str(tmp_path))
    assert len(report.artifacts) == 1
    assert report.artifacts[0].last_committed is None
    assert report.most_recent is None
    assert report.most_recent_by_type() == {}


def test_recency_excludes_unknown_documents(tmp_path):
    _init(tmp_path)
    corpus = tmp_path / "rac"
    corpus.mkdir(parents=True)
    (corpus / "prose.md").write_text("# Notes\n\nJust prose.\n", encoding="utf-8")
    (corpus / "r.md").write_text(_REQUIREMENT.format(title="R"), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "--quiet", "-m", "init", when="2026-01-01T00:00:00+00:00")

    report = artifact_recency(str(tmp_path))
    # Only the recognised requirement is tracked, not the prose document.
    assert [Path(a.path).name for a in report.artifacts] == ["r.md"]


def test_recency_to_dict_shape(tmp_path):
    _init(tmp_path)
    corpus = tmp_path / "rac" / "requirements"
    corpus.mkdir(parents=True)
    (corpus / "a.md").write_text(_REQUIREMENT.format(title="A"), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "--quiet", "-m", "init", when="2026-01-01T12:00:00+00:00")

    payload = artifact_recency(str(tmp_path)).to_dict()
    assert payload["schema_version"] == "1"
    assert payload["most_recent"] == "2026-01-01T12:00:00+00:00"
    assert payload["by_type"]["requirement"] == "2026-01-01T12:00:00+00:00"
    assert payload["artifacts"][0]["type"] == "requirement"
    assert payload["artifacts"][0]["last_committed"] == "2026-01-01T12:00:00+00:00"
