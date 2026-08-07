from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME = settings.MAIL_FROM_NAME,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
)

async def send_appointment_email(
    email_to: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    start_time: str,
    end_time: str,
):
    """ Send email notification for appointment confirmation. """
    message = MessageSchema(
        subject="Appointment Scheduled Successfully",
        recipients=[email_to],
        body = f"""
        Dear {patient_name},

        Your appointment has been scheduled successfully.

        Doctor: {doctor_name}
        Date: {appointment_date}
        Time: {start_time} - {end_time}

        Please make sure to arrive on time for your appointment.

        Thank you,
        Hospital Management 
        """,
        subtype=MessageType.PLAIN
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_cancellation_email(
    email_to: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    start_time: str,
    end_time: str,
):  
    """ Send email notification for appointment cancellation"""
    message = MessageSchema(
        subject="Appointment Cancelled Successfully",
        recipients=[email_to],
        body = f"""
        Dear {patient_name},
        
        Your appointment has been cancelled successfully.

        Doctor: {doctor_name}
        Date: {appointment_date}
        Time: {start_time} - {end_time}

        Thank you,
        Hospital Management 
        """
    )
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_appointment_reschedule_email(
    email_to: str,
    patient_name: str,
    doctor_name: str,
    old_appointment_date: str,
    old_start_time: str,
    old_end_time: str,
    new_appointment_date: str,
    new_start_time: str,
    new_end_time: str,
): 
    """ Send email notification for appointment rescheduling"""
    message = MessageSchema(
        subject="Appointment Rescheduled Successfully",
        recipients=[email_to],
        body = f"""
        Dear {patient_name},

        Your appointment has been rescheduled successfully.

        Doctor: {doctor_name}
        Old Date: {old_appointment_date}
        Old Time: {old_start_time} - {old_end_time}

        New Date: {new_appointment_date}
        New Time: {new_start_time} - {new_end_time}

        Please make sure to arrive on time for your new appointment.

        Thank you,
        Hospital Management 
        """
    )
    fm = FastMail(conf)
    await fm.send_message(message)
