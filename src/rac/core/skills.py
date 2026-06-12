"""Bundled agent skill registry — `rac skill install` (v0.10.4).

The bundled skill set is a static registry with exactly one entry while
`rac-artifacts` is the only skill RAC ships; a skill-name argument on the CLI
arrives only when a second skill exists. Skill content ships as package
resources under :mod:`rac.skills` and is loaded with ``importlib.resources``,
mirroring how canonical templates ship under :mod:`rac.templates` (ADR-021),
so installation works from an installed wheel without the dogfood repository
and without AI or network access.

A registered skill whose packaged resource is absent is a broken installation
(:class:`SkillResourceMissing` → operational error), the same failure mode as
:class:`rac.core.templates.TemplateResourceMissing`.
"""

from __future__ import annotations

from importlib import resources

# Bundled skill names, in registry order. Callers take names from
# :func:`available_skills`; there is no user-supplied skill name yet.
BUNDLED_SKILLS = ("rac-artifacts",)


class SkillResourceMissing(Exception):
    """A registered skill's packaged resource is absent (operational error)."""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        super().__init__(
            f"packaged skill missing: {skill_name}; the RAC installation appears to be broken"
        )


def available_skills() -> list[str]:
    """Bundled skill names, in registry order."""
    return list(BUNDLED_SKILLS)


def load_skill(skill_name: str) -> bytes:
    """Return the packaged ``SKILL.md`` content for ``skill_name``.

    Bytes, not text: the installed file must be byte-identical to the
    packaged resource (REQ-007). Raises :class:`SkillResourceMissing` when
    the packaged resource is absent.
    """
    resource = resources.files("rac.skills").joinpath(skill_name, "SKILL.md")
    try:
        return resource.read_bytes()
    except FileNotFoundError as exc:
        raise SkillResourceMissing(skill_name) from exc
