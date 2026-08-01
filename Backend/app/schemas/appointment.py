from pydantic import BaseModel,Field, ConfigDict
from typing import Optional , List
from datetime import datetime
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

# Shared properties for Appointment model
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

class AppointmentInDBBase(AppointmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for compatibility with SQLAlchemy models

class Appointment(AppointmentInDBBase):
    pass

class AppointmentInDB(AppointmentInDBBase):
    pass

# Appointment model for detailed information including patient and doctor names
class AppointmentDetail(AppointmentInDBBase):
    patient_name: str
    doctor_name: str
    docker_specialization: str
