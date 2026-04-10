from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.consultation import Consultation
    from app.models.strategy import NutritionStrategy


class EvaluationStatus(str, Enum):
    calculated = "calculated"
    failed = "failed"


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    consultation_id: Mapped[int] = mapped_column(
        ForeignKey("consultations.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[EvaluationStatus] = mapped_column(
        SqlEnum(EvaluationStatus, name="evaluation_status", native_enum=False),
        nullable=False,
    )
    formula_set_version: Mapped[str] = mapped_column(String(100), nullable=False)
    equation_selection_policy: Mapped[str] = mapped_column(String(255), nullable=False)
    summary_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    warnings_payload: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    consultation: Mapped["Consultation"] = relationship(back_populates="evaluations")

    formula_results: Mapped[list["FormulaResult"]] = relationship(
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )
    strategies: Mapped[list["NutritionStrategy"]] = relationship(
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )


class FormulaResult(Base):
    __tablename__ = "formula_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    evaluation_id: Mapped[int] = mapped_column(
        ForeignKey("evaluations.id"),
        nullable=False,
        index=True,
    )
    formula_code: Mapped[str] = mapped_column(String(120), nullable=False)
    formula_version: Mapped[str] = mapped_column(String(50), nullable=False)
    formula_family: Mapped[str] = mapped_column(String(120), nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    output_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    evaluation: Mapped["Evaluation"] = relationship(back_populates="formula_results")
