from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.patient import PatientSex


class PatientRecordBase(BaseModel):
    primary_goal: str | None = None
    medical_history: str | None = None
    pathologies: str | None = None
    allergies: str | None = None
    intolerances: str | None = None
    dietary_restrictions: str | None = None
    food_preferences: str | None = None
    lifestyle_notes: str | None = None
    default_schedule: str | None = None
    general_observations: str | None = None


class PatientRecordUpsert(PatientRecordBase):
    pass


class PatientRecordRead(PatientRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    updated_by_user_id: int | None
    created_at: datetime
    updated_at: datetime


class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    sex: PatientSex
    birth_date: date
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None


class PatientCreate(PatientBase):
    record: PatientRecordUpsert | None = None


class PatientUpdate(PatientBase):
    pass


class PatientRead(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    record: PatientRecordRead | None


class MeasurementCreate(BaseModel):
    weight_kg: float | None = None
    height_cm: float | None = None
    waist_cm: float | None = None
    hip_cm: float | None = None
    body_fat_percentage: float | None = None
    activity_level: str | None = None


class MeasurementRead(MeasurementCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    consultation_id: int
    created_at: datetime


class ConsultationCreate(BaseModel):
    consultation_date: date
    reason: str | None = None
    adherence_report: str | None = None
    symptoms: str | None = None
    clinical_notes: str | None = None
    measurement: MeasurementCreate | None = None


class ConsultationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    nutritionist_user_id: int
    consultation_date: date
    reason: str | None
    adherence_report: str | None
    symptoms: str | None
    clinical_notes: str | None
    created_at: datetime
    measurement: MeasurementRead | None
