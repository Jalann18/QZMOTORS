"""
Comando: python manage.py send_recordatorios
Envía el correo #2 (recordatorio) a reservas cuya inspección es MAÑANA.
Ejecutar diariamente (ej: Railway Cron Job a las 20:00).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from landing.models import Reserva
from landing.emails import send_reminder_email


class Command(BaseCommand):
    help = "Envía correos de recordatorio a clientes con inspección mañana."

    def handle(self, *args, **kwargs):
        manana = timezone.localdate() + timedelta(days=1)

        reservas = Reserva.objects.filter(
            fecha=manana,
            estado='confirmada',
            recordatorio_enviado=False,
        )

        if not reservas.exists():
            self.stdout.write(self.style.WARNING(f"Sin inspecciones para mañana ({manana})."))
            return

        enviados = 0
        for reserva in reservas:
            ok = send_reminder_email(reserva)
            if ok:
                reserva.recordatorio_enviado = True
                reserva.save(update_fields=['recordatorio_enviado'])
                enviados += 1
                self.stdout.write(self.style.SUCCESS(f"  ✅ Recordatorio → {reserva.email} ({reserva.orden})"))
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ Error → {reserva.email} ({reserva.orden})"))

        self.stdout.write(self.style.SUCCESS(f"\n{enviados}/{reservas.count()} recordatorios enviados."))
