"""add patients and consultations

Revision ID: 20260408_0002
Revises: 20260408_0001
Create Date: 2026-04-08 00:10:00
"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260408_0002"
down_revision = "20260408_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "patients" not in existing_tables:
        op.create_table(
            "patients",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("first_name", sa.String(length=120), nullable=False),
            sa.Column("last_name", sa.String(length=120), nullable=False),
            sa.Column("sex", sa.String(length=20), nullable=False),
            sa.Column("birth_date", sa.Date(), nullable=False),
            sa.Column("phone", sa.String(length=50), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_patients_id", "patients", ["id"], unique=False)
        op.create_index("ix_patients_email", "patients", ["email"], unique=False)

    if "patient_records" not in existing_tables:
        op.create_table(
            "patient_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
            sa.Column("primary_goal", sa.String(length=255), nullable=True),
            sa.Column("medical_history", sa.Text(), nullable=True),
            sa.Column("pathologies", sa.Text(), nullable=True),
            sa.Column("allergies", sa.Text(), nullable=True),
            sa.Column("intolerances", sa.Text(), nullable=True),
            sa.Column("dietary_restrictions", sa.Text(), nullable=True),
            sa.Column("food_preferences", sa.Text(), nullable=True),
            sa.Column("lifestyle_notes", sa.Text(), nullable=True),
            sa.Column("default_schedule", sa.Text(), nullable=True),
            sa.Column("general_observations", sa.Text(), nullable=True),
            sa.Column("updated_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("patient_id", name="uq_patient_records_patient_id"),
        )

    if "consultations" not in existing_tables:
        op.create_table(
            "consultations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
            sa.Column(
                "nutritionist_user_id",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=False,
            ),
            sa.Column("consultation_date", sa.Date(), nullable=False),
            sa.Column("reason", sa.String(length=255), nullable=True),
            sa.Column("adherence_report", sa.Text(), nullable=True),
            sa.Column("symptoms", sa.Text(), nullable=True),
            sa.Column("clinical_notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_consultations_id", "consultations", ["id"], unique=False)
        op.create_index(
            "ix_consultations_patient_id",
            "consultations",
            ["patient_id"],
            unique=False,
        )

    if "measurements" not in existing_tables:
        op.create_table(
            "measurements",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "consultation_id",
                sa.Integer(),
                sa.ForeignKey("consultations.id"),
                nullable=False,
            ),
            sa.Column("weight_kg", sa.Float(), nullable=True),
            sa.Column("height_cm", sa.Float(), nullable=True),
            sa.Column("waist_cm", sa.Float(), nullable=True),
            sa.Column("hip_cm", sa.Float(), nullable=True),
            sa.Column("body_fat_percentage", sa.Float(), nullable=True),
            sa.Column("activity_level", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("consultation_id", name="uq_measurements_consultation_id"),
        )
        op.create_index("ix_measurements_id", "measurements", ["id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "measurements" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("measurements")}
        if "ix_measurements_id" in indexes:
            op.drop_index("ix_measurements_id", table_name="measurements")
        op.drop_table("measurements")

    if "consultations" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("consultations")}
        if "ix_consultations_patient_id" in indexes:
            op.drop_index("ix_consultations_patient_id", table_name="consultations")
        if "ix_consultations_id" in indexes:
            op.drop_index("ix_consultations_id", table_name="consultations")
        op.drop_table("consultations")

    if "patient_records" in existing_tables:
        op.drop_table("patient_records")

    if "patients" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("patients")}
        if "ix_patients_email" in indexes:
            op.drop_index("ix_patients_email", table_name="patients")
        if "ix_patients_id" in indexes:
            op.drop_index("ix_patients_id", table_name="patients")
        op.drop_table("patients")
