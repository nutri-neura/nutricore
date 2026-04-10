from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.consultation import Consultation, Measurement
from app.models.distribution import MealDistribution
from app.models.evaluation import Evaluation
from app.models.meal_plan import MealPlan, MealPlanMeal
from app.models.patient import Patient, PatientRecord
from app.models.slot_selection import MealPlanSlotSelection
from app.models.strategy import NutritionStrategy


def list_patients(db: Session) -> list[Patient]:
    return list(
        db.scalars(
            select(Patient)
            .options(joinedload(Patient.record))
            .order_by(Patient.created_at.desc())
        ).unique()
    )


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.scalar(
        select(Patient)
        .where(Patient.id == patient_id)
        .options(joinedload(Patient.record))
    )


def get_patient_with_history(db: Session, patient_id: int) -> Patient | None:
    return db.scalar(
        select(Patient)
        .where(Patient.id == patient_id)
        .options(
            joinedload(Patient.record),
            joinedload(Patient.consultations)
            .joinedload(Consultation.measurement),
            joinedload(Patient.consultations)
            .joinedload(Consultation.evaluations)
            .joinedload(Evaluation.strategies)
            .joinedload(NutritionStrategy.meal_distributions)
            .joinedload(MealDistribution.meal_plans)
            .joinedload(MealPlan.meals)
            .joinedload(MealPlanMeal.slot_selections)
            .joinedload(MealPlanSlotSelection.food_item),
        )
    )


def create_patient(db: Session, **kwargs) -> Patient:
    patient = Patient(**kwargs)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient: Patient, **kwargs) -> Patient:
    for key, value in kwargs.items():
        setattr(patient, key, value)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def upsert_patient_record(
    db: Session,
    patient: Patient,
    *,
    updated_by_user_id: int,
    **kwargs,
) -> PatientRecord:
    record = patient.record
    if record is None:
        record = PatientRecord(
            patient_id=patient.id,
            updated_by_user_id=updated_by_user_id,
            **kwargs,
        )
        db.add(record)
    else:
        for key, value in kwargs.items():
            setattr(record, key, value)
        record.updated_by_user_id = updated_by_user_id
        db.add(record)

    db.commit()
    db.refresh(record)
    return record


def create_consultation(
    db: Session,
    *,
    patient_id: int,
    nutritionist_user_id: int,
    consultation_date,
    reason: str | None,
    adherence_report: str | None,
    symptoms: str | None,
    clinical_notes: str | None,
    measurement_payload: dict | None,
) -> Consultation:
    consultation = Consultation(
        patient_id=patient_id,
        nutritionist_user_id=nutritionist_user_id,
        consultation_date=consultation_date,
        reason=reason,
        adherence_report=adherence_report,
        symptoms=symptoms,
        clinical_notes=clinical_notes,
    )
    db.add(consultation)
    db.flush()

    if measurement_payload is not None:
        measurement = Measurement(
            consultation_id=consultation.id,
            **measurement_payload,
        )
        db.add(measurement)

    db.commit()
    db.refresh(consultation)
    return db.scalar(
        select(Consultation)
        .where(Consultation.id == consultation.id)
        .options(joinedload(Consultation.measurement))
    )


def list_consultations_for_patient(db: Session, patient_id: int) -> list[Consultation]:
    return list(
        db.scalars(
            select(Consultation)
            .where(Consultation.patient_id == patient_id)
            .options(joinedload(Consultation.measurement))
            .order_by(Consultation.consultation_date.desc(), Consultation.id.desc())
        ).unique()
    )


def get_consultation(db: Session, consultation_id: int) -> Consultation | None:
    return db.scalar(
        select(Consultation)
        .where(Consultation.id == consultation_id)
        .options(joinedload(Consultation.measurement))
    )
