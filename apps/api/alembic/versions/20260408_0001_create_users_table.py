"""create users table

Revision ID: 20260408_0001
Revises: None
Create Date: 2026-04-08 00:00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

revision = "20260408_0001"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum(
    "admin",
    "nutriologo",
    "asistente",
    "recepcionista",
    name="user_role",
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    enum_exists = bind.execute(text("SELECT to_regtype('user_role') IS NOT NULL")).scalar()
    if not enum_exists:
        user_role.create(bind, checkfirst=True)

    if "users" not in inspector.get_table_names():
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column(
                "role",
                sa.Enum(
                    "admin",
                    "nutriologo",
                    "asistente",
                    "recepcionista",
                    name="user_role",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )

    indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_email" not in indexes:
        op.create_index("ix_users_email", "users", ["email"], unique=True)
    if "ix_users_id" not in indexes:
        op.create_index("ix_users_id", "users", ["id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "users" in inspector.get_table_names():
        indexes = {index["name"] for index in inspector.get_indexes("users")}
        if "ix_users_id" in indexes:
            op.drop_index("ix_users_id", table_name="users")
        if "ix_users_email" in indexes:
            op.drop_index("ix_users_email", table_name="users")
        op.drop_table("users")

    user_role.drop(bind, checkfirst=True)
