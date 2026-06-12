"""Minimal stand-in for the Meridian PostgreSQL connection.

This is not a real database. It records every statement it is asked to execute
so the demo can show, mechanically, whether the deletion path issued a hard
``DELETE`` or a soft-delete ``UPDATE``. The real service uses psycopg; the
surface here is deliberately the same shape (``execute(sql, params)``).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Statement:
    sql: str
    params: tuple


@dataclass
class Connection:
    """A fake connection that remembers the statements run against it."""

    executed: list[Statement] = field(default_factory=list)

    def execute(self, sql: str, params: tuple = ()) -> None:
        self.executed.append(Statement(sql=sql.strip(), params=params))

    def last_sql(self) -> str:
        return self.executed[-1].sql if self.executed else ""
