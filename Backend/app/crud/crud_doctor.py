from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, time
from app.db.models import Doctor, Appointment, Patient
from app.schemas.doctor import DoctorCreate, DoctorUpdate, AvailabilityCreate, Availability
from app.crud.crud_base import CRUDBase

class CRUDDoctor(CRUDBase[Doctor, DoctorCreate, DoctorUpdate]):

    def get_by_email(self, db: Session, *, email: str) -> Optional[Doctor]:
        return db.query(Doctor).filter(Doctor.email == email).first()

    def get_by_specialization(self, db: Session, *, specialization: str) -> List[Doctor]:
        return db.query(Doctor).filter(Doctor.specialization == specialization).all()

    def get_with_availability(self, db: Session, *, doctor_id: int) -> Optional[Doctor]:
        return db.query(Doctor).options(joinedload(Doctor.availability)).filter(Doctor.id == doctor_id).first()

    def add_availability(self, db: Session, *, doctor_id: int, availability_in: AvailabilityCreate) -> Doctor:
        db_availability = Availability(**availability_in.model_dump(), doctor_id=doctor_id)
        db.add(db_availability)
        db.commit()

        return self.get_with_availability(db, doctor_id=doctor_id)

    def check_availability(self, db: Session, *, doctor_id: int, start_time: datetime, end_time: datetime) -> bool:
        day_of_week = start_time.weekday()  # Monday is 0 and Sunday is 6

        availability = db.query(Availability).filter(
            Availability.doctor_id == doctor_id,
            Availability.day_of_week == day_of_week,
            Availability.is_available == True,
            Availability.start_time <= start_time.time(),
            Availability.end_time >= end_time.time()
        ).first()

        return availability is not None

    def get_available_slots(self, db: Session, *, doctor_id: int, date: datetime) -> List[Dict[str, Any]]:
        day_of_week = date.weekday()  # Monday is 0 and Sunday is 6

        availabilities = db.query(Availability).filter(
            Availability.doctor_id == doctor_id,
            Availability.day_of_week == day_of_week,
            Availability.is_available == True
        ).first()

        if not availabilities:
            return []

        start_of_day = datetime.combine(date.date(), time.min)
        end_of_day = datetime.combine(date.date(), time.max)

        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time >= start_of_day,
            Appointment.end_time <= end_of_day,
            Appointment.status != "cancelled"
        ).all()

        slots = []

        for availability in availabilities:
            current_time = datetime.combine(date.date(), availability.start_time)
            end_time = datetime.combine(date.date(), availability.end_time)

            while current_time + timedelta(minutes=30) <= end_time:
                slot_end_time = current_time + timedelta(minutes=30)

                is_available = True

                for appointment in appointments:
                    if not (slot_end_time <= appointment.start_time or current_time >= appointment.end_time):
                        is_available = False
                        break

                if is_available:
                    slots.append({
                        "start_time": current_time,
                        "end_time": slot_end_time,
                        "is_available": True
                    })

                current_time += slot_end_time
        return slots

doctor = CRUDDoctor(Doctor)
