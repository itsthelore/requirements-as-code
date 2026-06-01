"""Shared pytest fixtures: paths to the Markdown fixture files."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


def fixture_path(*parts: str) -> str:
    return str(FIXTURES.joinpath(*parts))
