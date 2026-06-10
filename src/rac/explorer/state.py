"""Explorer UI state — what the widgets render (v0.8.0).

Frozen, presentation-ready snapshots translated from Core models by the
adapter (ADR-015). Widgets and screens consume these types only; they never
import Core models, and this module never imports Textual.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadProgressState:
    """One progress update while the repository loads."""

    phase: str
    completed: int
    total: int | None
    label: str  # presentation-ready, e.g. "Scanning artifacts (12/95)"


@dataclass(frozen=True)
class RepositorySummaryState:
    """The repository summary the v0.8.0 shell renders."""

    directory: str
    artifact_total: int
    by_type: tuple[tuple[str, int], ...]  # (type, count), zero counts omitted
    relationship_total: int
    broken_relationships: int
    error_count: int
    warning_count: int
    health_score: int


@dataclass(frozen=True)
class LoadErrorState:
    """A recoverable failure: the shell shows it and offers retry."""

    title: str
    detail: str
    can_retry: bool
