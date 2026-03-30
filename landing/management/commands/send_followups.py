"""
Comando: python manage.py send_followups
Envía el correo #3 (post-inspección) a reservas cuya fecha fue AYER.
Ejecutar diariamente (ej: Railway Cron Job a las 10:00).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from landing.models import Reserva
from landing.emails import send_followup_email


class Command(BaseCommand):
    help = "Envía correos de seguimiento a clientes cuya inspección fue ayer."

    def handle(self, *args, **kwargs):
        ayer = timezone.localdate() - timedelta(days=1)

        reservas = Reserva.objects.filter(
            fecha=ayer,
            estado='confirmada',
            followup_enviado=False,
        )

        if not reservas.exists():
            self.stdout.write(self.style.WARNING(f"Sin inspecciones de ayer ({ayer})."))
            return

        enviados = 0
        for reserva in reservas:
            ok = send_followup_email(reserva)
            if ok:
                reserva.followup_enviado = True
                reserva.save(update_fields=['followup_enviado'])
                enviados += 1
                self.stdout.write(self.style.SUCCESS(f"  ✅ Follow-up → {reserva.email} ({reserva.orden})"))
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ Error → {reserva.email} ({reserva.orden})"))

        self.stdout.write(self.style.SUCCESS(f"\n{enviados}/{reservas.count()} follow-ups enviados."))
