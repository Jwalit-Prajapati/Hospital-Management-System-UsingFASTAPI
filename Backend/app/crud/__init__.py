"""
CRUD package.
"""
from .crud_base import CRUDBase
from .crud_patient import patient
from .crud_doctor import doctor
from .crud_appointment import appointment
from .crud_user import user

__all__ = ["CRUDBase", "patient", "doctor", "appointment", "user"]