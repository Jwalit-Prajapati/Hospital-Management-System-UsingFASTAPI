from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user
from app.core.config import settings
from app.crud.crud_patient import patient
from app.schemas.patient import Patient, PatientCreate, PatientUpdate
from app.schemas.user import User
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[Patient], status_code=status.HTTP_200_OK)
def read_patients(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
) -> Any:

    patients = patient.get_multi(db, skip=skip, limit=limit)
    return patients

@router.post("/", response_model=Patient, status_code=status.HTTP_201_CREATED)
def create_patient(
    *, db: Session = Depends(get_db),
    patient_in: PatientCreate,
) -> Any:
    existing_patient = patient.get_by_email(db, email = patient_in.email)
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The patient with this email already exists in the system.",
        )

    try:
        patient_obj = patient.create(db, obj_in=patient_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating patient.",
        )
    return patient_obj

@router.get("/search",response_model = List[Patient], status_code=status.HTTP_200_OK)
def search_patients( * , db: Session = Depends(get_db), query: str) -> Any:
    patients = patient.search(db, query=query)
    return patients

@router.get("/{id}",response_model=Patient, status_code=status.HTTP_200_OK)
def read_patient(
    *, db: Session = Depends(get_db),id: int) -> Any:
    patient_obj = patient.get(db, id=id)
    if not patient_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return patient_obj

@router.put("/{id}",response_model= Patient, status_code=status.HTTP_200_OK)
def update_patient(
    *, db: Session = Depends(get_db),
    id: int, patient_in: PatientUpdate
) -> Any:
    patient_obj = patient.get(db, id = id)

    if not patient_obj:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Patient not found.",
        )

    if (
        patient_in.email is not None
        and patient_in.email != patient_obj.email
        ):
        existing = patient.get_by_email(db, email=patient_in.email)
        if existing:
            raise HTTPException(
              status_code=400,
                detail="The email is already registered to another patient."
            )

    try:
        patient_obj = patient.update(db, db_obj=patient_obj, obj_in=patient_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating patient.",
        )
    return patient_obj

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(*, db : Session = Depends(get_db), id : int) -> None:
    patient_obj = patient.get(db, id=id)
    if not patient_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )
    patient.remove(db, id=id)
