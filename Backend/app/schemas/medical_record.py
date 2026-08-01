from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Shared properties for MedicalRecord model
class MedicalRecordBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None

class MedicalRecordInDBBase(MedicalRecordBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for compatibility with SQLAlchemy models

class MedicalRecord(MedicalRecordInDBBase):
    pass

class MedicalRecordInDB(MedicalRecordInDBBase):
    pass
