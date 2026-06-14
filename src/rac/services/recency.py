"""Git-derived artifact recency (v0.13.2, ADR-045).

When was each artifact last written? RAC artifacts carry no timestamp, and
adding one would mean a schema change, hand-kept dates that drift, and the
work-status modelling ADR-017 rejects. Git already records exactly when every
file last changed, so recency is *derived* from `git log`, never stored.

This is the second narrow git touchpoint in the package, alongside
`revisions.py` (ADR-043): read-only, offline, no `.git` mutation. It answers
"unknown" (``None``) rather than raising when git is unavailable, the
directory is not a repository, or a file is untracked or uncommitted —
recency is advisory, never required.

Recency is a *capture-cadence* signal — when product knowledge was last
written — explicitly not a work-status or due-date signal, so consumers (the
cadence nudge, v0.13.3) stay inside ADR-017.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rac.services.index import build_repository_index


def _run_git(args: list[str], cwd: str) -> subprocess.CompletedProcess[str] | None:
    """Run git, capturing text output; ``None`` when git is not on PATH."""
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False, text=True)
    except FileNotFoundError:  # no git binary
        return None


def _repository_root(directory: str) -> str | None:
    """The work-tree root containing ``directory``, or ``None`` if not a repo."""
    result = _run_git(["rev-parse", "--show-toplevel"], cwd=directory)
    if result is None or result.returncode != 0:
        return None
    return result.stdout.strip()


def _last_committed(repo_root: str, path: str) -> datetime | None:
    """Commit time of the most recent change to ``path``, or ``None``.

    Uses ``git log -1 --format=%cI`` (ISO-8601, timezone-aware). An empty
    result means the file is untracked or uncommitted.
    """
    abspath = Path(path).resolve()
    try:
        pathspec = str(abspath.relative_to(Path(repo_root).resolve()))
    except ValueError:  # path lies outside the work tree; pass it through
        pathspec = str(abspath)
    result = _run_git(["log", "-1", "--format=%cI", "--", pathspec], cwd=repo_root)
    if result is None or result.returncode != 0:
        return None
    stamp = result.stdout.strip()
    if not stamp:
        return None
    try:
        return datetime.fromisoformat(stamp)
    except ValueError:  # unexpected git output; treat as unknown
        return None


@dataclass
class ArtifactRecency:
    """One artifact's last-authored time, or ``None`` when git does not know."""

    path: str
    artifact_type: str
    last_committed: datetime | None


@dataclass
class RecencyReport:
    """Corpus recency: per-artifact last-authored times and aggregates."""

    directory: str
    recursive: bool
    artifacts: list[ArtifactRecency]

    @property
    def most_recent(self) -> datetime | None:
        """The newest last-authored time across all artifacts, or ``None``."""
        known = [a.last_committed for a in self.artifacts if a.last_committed is not None]
        return max(known) if known else None

    def most_recent_by_type(self) -> dict[str, datetime]:
        """Newest last-authored time per artifact type (unknowns omitted)."""
        result: dict[str, datetime] = {}
        for a in self.artifacts:
            if a.last_committed is None:
                continue
            current = result.get(a.artifact_type)
            if current is None or a.last_committed > current:
                result[a.artifact_type] = a.last_committed
        return result

    def to_dict(self) -> dict:
        most_recent = self.most_recent
        return {
            "schema_version": "1",
            "directory": self.directory,
            "recursive": self.recursive,
            "most_recent": most_recent.isoformat() if most_recent else None,
            "by_type": {t: ts.isoformat() for t, ts in sorted(self.most_recent_by_type().items())},
            "artifacts": [
                {
                    "path": a.path,
                    "type": a.artifact_type,
                    "last_committed": (a.last_committed.isoformat() if a.last_committed else None),
                }
                for a in self.artifacts
            ],
        }


def artifact_recency(directory: str, recursive: bool = True) -> RecencyReport:
    """Recency for every recognised artifact under ``directory``.

    Derives each artifact's last-committed time from git. Outside a git
    repository, or for untracked files, the time is ``None`` ("unknown") — no
    exception crosses the boundary. Unknown-type documents are excluded;
    recency is about product-knowledge artifacts.
    """
    index = build_repository_index(directory, recursive=recursive)
    entries = [e for e in index.artifacts if e.type != "unknown"]
    repo_root = _repository_root(directory)

    artifacts: list[ArtifactRecency] = []
    for entry in entries:
        last = _last_committed(repo_root, entry.path) if repo_root is not None else None
        artifacts.append(
            ArtifactRecency(path=entry.path, artifact_type=entry.type, last_committed=last)
        )
    return RecencyReport(directory=directory, recursive=recursive, artifacts=artifacts)
