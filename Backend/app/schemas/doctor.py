from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime, time

#Shared properties for Doctor model
class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    specialization: str

#properties for Doctor model when creating a new doctor
class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None

class DoctorInDBBase(DoctorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for compatibility with SQLAlchemy models

class Doctor(DoctorInDBBase):
    pass

class DoctorInDB(DoctorInDBBase):
    pass

# Availability model for doctors
class AvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    is_available: bool = True

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityUpdate(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None

class AvailabilityInDBBase(AvailabilityBase):
    id: int
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for compatibility with SQLAlchemy models

class Availability(AvailabilityInDBBase):
    pass

class DoctorWithAvailability(Doctor):
    availabilities: list[Availability] = []