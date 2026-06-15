"""`no_grounding` arm — the control / floor.

Supplies the answering model with NO decision grounding (empty context). It
measures the floor: how often the answering model adheres to prior decisions
from parametric knowledge alone. Every grounded arm must beat this.

With the offline scripted answering model (which reads only the grounding and
has no parametric knowledge) this arm proceeds on everything, so it scores at
the floor — adhering only where the correct behaviour is to proceed (the
negative control). With the real Claude answering model it reflects genuine
parametric adherence.
"""

from __future__ import annotations

from .base import CorpusArtifact, GroundingContext, Provider


class NoGroundingProvider(Provider):
    name = "no_grounding"

    def prepare(self, corpus: list[CorpusArtifact]) -> None:
        # The single symmetric grounding opportunity, populated with nothing.
        self._grounding = GroundingContext(text="", artifacts_supplied=(), token_estimate=0)
