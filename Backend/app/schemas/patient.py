from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime, date

#Shared properties for Patient model
class PatientBase(BaseModel):
    first_name:str
    last_name:str
    date_of_birth:date
    email: EmailStr
    phone: str
    address: str
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None

# Properties for Patient model when creating a new patient
class PatientCreate(PatientBase):
    pass

# Patient to recieve on patient update
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None

# Properties shared by models stored in DB
class PatientInDBBase(PatientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for compatibility with SQLAlchemy models

# Properties for Patient model when returning patient data in API responses
class Patient(PatientInDBBase):
    pass

# Properties for Patient model when storing patient data in the database
class PatientInDB(PatientInDBBase):
    pass