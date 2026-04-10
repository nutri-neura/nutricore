from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.patient import (
    create_consultation,
    create_patient,
    get_consultation,
    get_patient,
    list_consultations_for_patient,
    list_patients,
    update_patient,
    upsert_patient_record,
)
from app.schemas.history import PatientHistoryRead
from app.schemas.patient import (
    ConsultationCreate,
    ConsultationRead,
    PatientCreate,
    PatientRead,
    PatientRecordRead,
    PatientRecordUpsert,
    PatientUpdate,
)
from app.services.history import read_patient_history

router = APIRouter()


@router.get("", response_model=list[PatientRead])
def read_patients(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PatientRead]:
    return [PatientRead.model_validate(patient) for patient in list_patients(db)]


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(
    payload: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientRead:
    patient = create_patient(
        db,
        first_name=payload.first_name,
        last_name=payload.last_name,
        sex=payload.sex.value,
        birth_date=payload.birth_date,
        phone=payload.phone,
        email=payload.email,
    )

    if payload.record is not None:
        upsert_patient_record(
            db,
            patient,
            updated_by_user_id=current_user.id,
            **payload.record.model_dump(),
        )
        patient = get_patient(db, patient.id)

    return PatientRead.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientRead)
def read_patient(
    patient_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return PatientRead.model_validate(patient)


@router.get("/{patient_id}/history", response_model=PatientHistoryRead)
def read_patient_history_endpoint(
    patient_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientHistoryRead:
    payload = read_patient_history(db, patient_id=patient_id)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return PatientHistoryRead.model_validate(payload)


@router.put("/{patient_id}", response_model=PatientRead)
def update_patient_endpoint(
    patient_id: int,
    payload: PatientUpdate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    updated_patient = update_patient(db, patient, **payload.model_dump())
    return PatientRead.model_validate(updated_patient)


@router.put("/{patient_id}/record", response_model=PatientRecordRead)
def upsert_patient_record_endpoint(
    patient_id: int,
    payload: PatientRecordUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PatientRecordRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    record = upsert_patient_record(
        db,
        patient,
        updated_by_user_id=current_user.id,
        **payload.model_dump(),
    )
    return PatientRecordRead.model_validate(record)


@router.get("/{patient_id}/consultations", response_model=list[ConsultationRead])
def read_patient_consultations(
    patient_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConsultationRead]:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    consultations = list_consultations_for_patient(db, patient_id)
    return [ConsultationRead.model_validate(item) for item in consultations]


@router.post(
    "/{patient_id}/consultations",
    response_model=ConsultationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_consultation(
    patient_id: int,
    payload: ConsultationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConsultationRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    consultation = create_consultation(
        db,
        patient_id=patient_id,
        nutritionist_user_id=current_user.id,
        consultation_date=payload.consultation_date,
        reason=payload.reason,
        adherence_report=payload.adherence_report,
        symptoms=payload.symptoms,
        clinical_notes=payload.clinical_notes,
        measurement_payload=payload.measurement.model_dump() if payload.measurement else None,
    )
    return ConsultationRead.model_validate(consultation)


@router.get("/consultations/{consultation_id}", response_model=ConsultationRead)
def read_consultation(
    consultation_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConsultationRead:
    consultation = get_consultation(db, consultation_id)
    if consultation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found",
        )
    return ConsultationRead.model_validate(consultation)
