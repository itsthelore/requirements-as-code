"""Data-access layer for Meridian user accounts.

Backed by the ``users`` table in PostgreSQL. Active-account queries filter on
``deleted_at IS NULL``; the ``deleted_at`` column is the account-closure marker
used across the service.
"""

from __future__ import annotations

from datetime import UTC, datetime

from .db import Connection


class UserRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def create(self, user_id: str, email: str) -> None:
        self._conn.execute(
            "INSERT INTO users (id, email, created_at) VALUES (%s, %s, %s)",
            (user_id, email, datetime.now(UTC)),
        )

    def get(self, user_id: str) -> None:
        self._conn.execute(
            "SELECT id, email, created_at FROM users WHERE id = %s AND deleted_at IS NULL",
            (user_id,),
        )

    def list_active(self) -> None:
        self._conn.execute(
            "SELECT id, email, created_at FROM users WHERE deleted_at IS NULL ORDER BY created_at",
            (),
        )

    def delete(self, user_id: str) -> None:
        """Close the account identified by ``user_id``.

        TODO(meridian): implement account deletion for DELETE /users/{id}.
        """
        raise NotImplementedError
