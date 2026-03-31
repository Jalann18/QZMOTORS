"""
emails.py — Sistema de correos de QZ Motors
3 correos: confirmación, recordatorio (día anterior) y seguimiento post-inspección.

Para activar, configura en .env:
    EMAIL_HOST_USER=zuninoweb.qz@gmail.com
    EMAIL_HOST_PASSWORD=tu_contrasena_de_app_gmail
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading
import logging

logger = logging.getLogger(__name__)

QZ_EMAIL = settings.DEFAULT_FROM_EMAIL
QZ_PHONE = "+56 9 4255 6282"
QZ_INSTAGRAM = "@qz.motors"


def _send_sync(subject, to_email, template_name, context):
    """Función síncrona que realiza el envío real."""
    try:
        html_body = render_to_string(f"landing/emails/{template_name}", context)
        send_mail(
            subject=subject,
            message="",          # Texto plano vacío — usamos solo HTML
            from_email=QZ_EMAIL,
            recipient_list=[to_email],
            html_message=html_body,
            fail_silently=False,
        )
        logger.info(f"[EMAIL SUCCESS] '{subject}' enviado a {to_email}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL ERROR] Falló '{subject}' a {to_email}: {e}")
        return False


def _send(subject, to_email, template_name, context):
    """Lanza el envío en un hilo separado para no bloquear el proceso principal."""
    thread = threading.Thread(
        target=_send_sync, 
        args=(subject, to_email, template_name, context)
    )
    thread.daemon = True # El hilo muere si el proceso principal muere
    thread.start()
    logger.info(f"[EMAIL THREAD] Lanzado hilo para '{subject}' a {to_email}")
    return True # Retorna True de inmediato


# ─────────────────────────────────────────────
# CORREO #1 — Confirmación de reserva
# Disparar en: checkout_return (Flow OK) o checkout_process (presencial)
# ─────────────────────────────────────────────
def send_confirmation_email(reserva):
    subject = f"✅ Reserva Confirmada — {reserva.orden} | QZ Motors"
    context = {
        "reserva": reserva,
        "qz_phone": QZ_PHONE,
        "qz_instagram": QZ_INSTAGRAM,
    }
    return _send(subject, reserva.email, "confirmacion.html", context)


# ─────────────────────────────────────────────
# CORREO #2 — Recordatorio (día anterior)
# Disparar con: python manage.py send_recordatorios
# (ejecutar diariamente con Railway Cron o similar)
# ─────────────────────────────────────────────
def send_reminder_email(reserva):
    subject = f"📅 Mañana es tu inspección — {reserva.patente} | QZ Motors"
    context = {
        "reserva": reserva,
        "qz_phone": QZ_PHONE,
        "qz_instagram": QZ_INSTAGRAM,
    }
    return _send(subject, reserva.email, "recordatorio.html", context)


# ─────────────────────────────────────────────
# CORREO #3 — Seguimiento post-inspección
# Disparar con: python manage.py send_followups
# (ejecutar diariamente con Railway Cron o similar)
# ─────────────────────────────────────────────
def send_followup_email(reserva):
    subject = f"⭐ ¿Cómo fue tu experiencia? | QZ Motors"
    context = {
        "reserva": reserva,
        "qz_phone": QZ_PHONE,
        "qz_instagram": QZ_INSTAGRAM,
    }
    return _send(subject, reserva.email, "followup.html", context)


# ─────────────────────────────────────────────
# CORREO #ADMIN — Aviso de nueva reserva/venta
# ─────────────────────────────────────────────
def send_admin_notification(reserva):
    subject = f"🚨 NUEVA VENTA — {reserva.orden} | {reserva.patente}"
    admin_email = "contacto@qzmotors.cl" # Correo oficial de QZ Motors
    context = {
        "reserva": reserva,
    }
    return _send(subject, admin_email, "admin_notification.html", context)
