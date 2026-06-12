"""Skill installation — `rac skill install` (v0.10.4).

``install_skill`` is the reusable installation capability: it owns resource
loading, the never-overwrite check, parent directory creation, and the result
model, so the CLI stays a thin adapter. The target layout is the documented
Claude Code project-level discovery path:
``<dir>/.claude/skills/<skill-name>/SKILL.md``.

Failure contract:

- existing skill file    → :class:`SkillFileExists` (refused; the existing
  file is left untouched — exit 1, per the v0.10.4 contract)
- missing packaged skill → :class:`~rac.core.skills.SkillResourceMissing`
  (operational; broken installation)

A nonexistent target directory is a usage error the CLI rejects before the
service runs (exit 2), matching every other path-taking command.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rac.core.skills import BUNDLED_SKILLS, load_skill

# The only bundled skill (v0.10.4). A skill-name parameter is introduced only
# when a second skill exists; until then the service installs this one.
SKILL_NAME = BUNDLED_SKILLS[0]


class SkillFileExists(Exception):
    """The target skill file already exists; RAC never overwrites it."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"{path} already exists; rac skill install never overwrites")


@dataclass
class InstalledSkill:
    """Result of one skill installation (stable JSON contract, ADR-007)."""

    skill: str
    path: str
    bytes_written: int

    def to_dict(self) -> dict:
        return {
            "schema_version": "1",
            "installed": True,
            "skill": self.skill,
            "path": self.path,
        }


def install_skill(target_dir: str) -> InstalledSkill:
    """Write the bundled skill into ``target_dir``'s Claude Code skill path.

    Parent directories are created as needed; an existing skill file is never
    overwritten. Raises :class:`SkillFileExists` when the target file already
    exists and :class:`~rac.core.skills.SkillResourceMissing` when the
    packaged resource is absent.
    """
    data = load_skill(SKILL_NAME)  # validates the installation first (cheap)
    dest = Path(target_dir) / ".claude" / "skills" / SKILL_NAME / "SKILL.md"
    if dest.exists():
        raise SkillFileExists(str(dest))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return InstalledSkill(skill=SKILL_NAME, path=str(dest), bytes_written=len(data))
