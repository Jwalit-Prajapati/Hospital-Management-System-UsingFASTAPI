from typing import Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from app.db.models import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from app.crud.crud_base import CRUDBase

class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):

    def get_by_email(self, db: Session, *, email: str) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.email == email).first()

    def create(self, db: Session,*, obj_in: PatientCreate) -> Patient:
        db_obj = Patient(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Patient, obj_in: Union[PatientUpdate, Dict[str, Any]]) -> Patient:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self,db: Session,*,id: int) -> Patient:
        obj = db.query(Patient).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

patient = CRUDPatient(Patient)
