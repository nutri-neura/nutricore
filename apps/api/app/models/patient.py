from __future__ import annotations

from datetime import UTC, date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.consultation import Consultation


class PatientSex(str, Enum):
    female = "female"
    male = "male"
    other = "other"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sex: Mapped[PatientSex] = mapped_column(
        SqlEnum(PatientSex, name="patient_sex", native_enum=False),
        nullable=False,
    )
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    record: Mapped["PatientRecord | None"] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
        uselist=False,
    )
    consultations: Mapped[list["Consultation"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
    )


class PatientRecord(Base):
    __tablename__ = "patient_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), unique=True, nullable=False)
    primary_goal: Mapped[str | None] = mapped_column(String(255))
    medical_history: Mapped[str | None] = mapped_column(Text)
    pathologies: Mapped[str | None] = mapped_column(Text)
    allergies: Mapped[str | None] = mapped_column(Text)
    intolerances: Mapped[str | None] = mapped_column(Text)
    dietary_restrictions: Mapped[str | None] = mapped_column(Text)
    food_preferences: Mapped[str | None] = mapped_column(Text)
    lifestyle_notes: Mapped[str | None] = mapped_column(Text)
    default_schedule: Mapped[str | None] = mapped_column(Text)
    general_observations: Mapped[str | None] = mapped_column(Text)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    patient: Mapped["Patient"] = relationship(back_populates="record")
