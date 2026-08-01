"""add explicit user roles

Revision ID: 8f4d1c2a9b10
Revises: 22a0b040bce3
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8f4d1c2a9b10"
down_revision: Union[str, Sequence[str], None] = "22a0b040bce3"
branch_labels = None
depends_on = None

user_role = sa.Enum("user", "admin", name="userrole")


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column("role", user_role, nullable=False, server_default="user"),
    )
    op.execute("UPDATE users SET role = 'admin' WHERE is_admin = true")
    op.alter_column("users", "role", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "role")
    user_role.drop(op.get_bind(), checkfirst=True)
