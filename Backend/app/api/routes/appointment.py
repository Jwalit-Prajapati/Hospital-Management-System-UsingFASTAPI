from typing import List, Any
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.api.deps import get_current_user
from app.crud.crud_appointment import appointment
from app.crud.crud_doctor import doctor
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatus, Appointment, AppointmentDetail
from app.schemas.user import User, UserRole
from app.db.session import get_db
from app.db.models import Patient, Doctor
from app.core.email import send_appointment_email, send_cancellation_email, send_appointment_reschedule_email

router = APIRouter()

@router.get("/", response_model=List[Appointment], status_code=status.HTTP_200_OK)
def read_appointments(
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100,
    current_user: User = Depends(get_current_user),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> Any:

    if (start_date is not None
        and end_date is not None
        and start_date > end_date
        ):
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date."
        )
    
    if current_user.role == UserRole.PATIENT:
        appointments = appointment.get_by_patient(
            db, patient_id = current_user.id,
            start_date=start_date, end_date=end_date,
            skip=skip, limit=limit
        )
    elif current_user.role == UserRole.DOCTOR:
        appointments = appointment.get_by_doctor(
            db, doctor_id = current_user.id,
            start_date=start_date, end_date=end_date,
            skip=skip, limit=limit
        )
    else:
        appointments = appointment.get_multi_with_detail(
            db, skip=skip, limit=limit,
            start_date=start_date, end_date=end_date
        )

    return appointments


@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(
    *, db: Session = Depends(get_db),
    appointment_in: AppointmentCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    is_doctor_available = doctor.check_availability(
        db, doctor_id=appointment_in.doctor_id,
        start_time=appointment_in.start_time,
        end_time=appointment_in.end_time
    )

    if not is_doctor_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor is not available at the requested time."
        )

    has_conflict = appointment.check_conflicts(
        db, doctor_id=appointment_in.doctor_id,
        start_time=appointment_in.start_time,
        end_time=appointment_in.end_time,appointment_id=None
    )

    if has_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested time slot conflicts with an existing appointment."
        )

    appointment_obj = appointment.create(db, obj_in=appointment_in)

    # Send email notification to patient and doctor
    patient_obj = db.query(Patient).filter(Patient.id == appointment_in.patient_id).first()
    doctor_obj = db.query(Doctor).filter(Doctor.id == appointment_in.doctor_id).first()

    if patient_obj and doctor_obj:
        background_tasks.add_task(
            send_appointment_email,
            email_to=patient_obj.email,
            patient_name=f"{patient_obj.first_name} {patient_obj.last_name}",
            doctor_name=f"{doctor_obj.first_name} {doctor_obj.last_name}",
            appointment_date=appointment_in.start_time.date(),
            start_time=appointment_in.start_time.time(),
            end_time=appointment_in.end_time.time(),
        )

    return appointment_obj

@router.get("/{id}",response_model=AppointmentDetail, status_code=status.HTTP_200_OK)
def read_appointment(
    *, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: int,
) -> Any:
    appointment_obj = appointment.get_with_detail(db, id=id)

    if not appointment_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found."
        )

    if current_user.role == UserRole.PATIENT and appointment_obj["patient_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this appointment."
        )

    if current_user.role == UserRole.DOCTOR and appointment_obj["doctor_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this appointment."
        )
    
    return appointment_obj

@router.put("/{id}", response_model=Appointment, status_code=status.HTTP_200_OK)
def update_appointment(
    *, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: int, appointment_in: AppointmentUpdate,
    background_tasks: BackgroundTasks,
) -> Any:
    appointment_obj = appointment.get(db, id=id)

    if not appointment_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found."
        )

    if current_user.role == UserRole.PATIENT and appointment_obj.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this appointment."
        )

    if appointment_in.start_time and appointment_in.end_time:
        is_doctor_available = doctor.check_availability(
            db, doctor_id=appointment_obj.doctor_id,
            start_time=appointment_in.start_time,
            end_time=appointment_in.end_time
        )

        if not is_doctor_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor is not available at the requested time."
            )

        has_conflict = appointment.check_conflicts(
            db, doctor_id=appointment_obj.doctor_id,
            start_time=appointment_in.start_time,
            end_time=appointment_in.end_time,
            appointment_id=id
        )

        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The requested time slot conflicts with an existing appointment."
            )

    try:
        old_start_time = appointment_obj.start_time
        old_end_time = appointment_obj.end_time

        appointment_obj = appointment.update(db, db_obj=appointment_obj, obj_in=appointment_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update appointment due to integrity constraints."
        )

    # Send email notification to patient and doctor if the appointment time has changed
    if appointment_in.start_time and appointment_in.end_time:
        patient_obj = db.query(Patient).filter(Patient.id == appointment_obj.patient_id).first()
        doctor_obj = db.query(Doctor).filter(Doctor.id == appointment_obj.doctor_id).first()

        if patient_obj and doctor_obj:
            background_tasks.add_task(
                send_appointment_reschedule_email,
                email_to=patient_obj.email,
                patient_name=f"{patient_obj.first_name} {patient_obj.last_name}",
                doctor_name=f"{doctor_obj.first_name} {doctor_obj.last_name}",
                old_appointment_date=old_start_time.date(),
                old_start_time=old_start_time.time(),
                old_end_time=old_end_time.time(),
                new_appointment_date=appointment_in.start_time.date(),
                new_start_time=appointment_in.start_time.time(),
                new_end_time=appointment_in.end_time.time(),
            )

    return appointment_obj

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(*, db : Session = Depends(get_db),id: int, background_tasks: BackgroundTasks) -> None:
    appointment_obj = appointment.get(db, id=id)

    if not appointment_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found."
        )

    try:
        appointment.remove(db, id=id)
        background_tasks.add_task(
            send_cancellation_email,
            email_to=appointment_obj.patient.email,
            patient_name=f"{appointment_obj.patient.first_name} {appointment_obj.patient.last_name}",
            doctor_name=f"{appointment_obj.doctor.first_name} {appointment_obj.doctor.last_name}",
            appointment_date=appointment_obj.start_time.date(),
            start_time=appointment_obj.start_time.time(),
            end_time=appointment_obj.end_time.time(),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete appointment due to integrity constraints."
        )

    return {"detail": "Appointment deleted successfully."}

@router.put("/{id}/status", response_model=Appointment, status_code=status.HTTP_200_OK)
def update_appointment_status(
    *, db: Session = Depends(get_db),
    id: int, status_in: AppointmentStatus,
    background_tasks: BackgroundTasks
) -> Any:
    appointment_obj = appointment.get(db, id = id)

    if not appointment_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found."
        )

    try:
        appointment_obj = appointment.update_status(db, id=id, status=status_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update appointment status due to integrity constraints."
        )

    if status_in == AppointmentStatus.CANCELLED:
        patient_obj = db.query(Patient).filter(Patient.id == appointment_obj.patient_id).first()
        doctor_obj = db.query(Doctor).filter(Doctor.id == appointment_obj.doctor_id).first()
        if patient_obj and doctor_obj:
            background_tasks.add_task(
                send_cancellation_email,
                email_to=patient_obj.email,
                patient_name=f"{patient_obj.first_name} {patient_obj.last_name}",
                doctor_name=f"{doctor_obj.first_name} {doctor_obj.last_name}",
                appointment_date=appointment_obj.start_time.date(),
                start_time=appointment_obj.start_time.time(),
                end_time=appointment_obj.end_time.time(),
            )

    return appointment_obj

@router.get("/doctor/{doctor_id}/available-slots", response_model=List[dict], status_code=status.HTTP_200_OK)
def get_available_slots(
    *,db: Session = Depends(get_db),
    doctor_id: int, date: datetime = Query(...)
) -> Any:

    try : 
        available_slots = doctor.get_available_slots(db, doctor_id=doctor_id, date=date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching available slots: {str(e)}"
        )

    if not available_slots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available slots found for the specified doctor on the given date."
        )
    return available_slots
