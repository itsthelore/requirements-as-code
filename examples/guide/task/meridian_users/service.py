"""Service layer for Meridian user accounts.

The deletion endpoint ``DELETE /users/{id}`` calls into ``close_account``.
"""

from __future__ import annotations

from .repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def close_account(self, user_id: str) -> None:
        """Handle DELETE /users/{id}: close the user's account."""
        self._repository.delete(user_id)
