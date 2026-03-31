from django.db import models


class Cita(models.Model):
    """Modelo original - mantenido por compatibilidad"""
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    patente = models.CharField(max_length=15)
    comuna = models.CharField(max_length=100)
    fecha = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.patente} - {self.fecha.strftime('%Y-%m-%d')}"


class Reserva(models.Model):
    """Modelo completo de reserva con todos los datos del checkout"""

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    METODO_CHOICES = [
        ('flow', 'Pago Online (Flow)'),
        ('presencial', 'Pago Presencial'),
    ]

    PLAN_CHOICES = [
        ('scanner', 'Scanner Automotriz'),
        ('completa', 'Inspección Completa 360°'),
        ('promo_2x1', 'Promo 2x1 Inspección Completa'),
    ]

    # Identificación
    orden = models.CharField(max_length=50, unique=True)

    # Datos del cliente
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    rut = models.CharField(max_length=15)
    telefono = models.CharField(max_length=20)

    # Ubicación
    comuna = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

    # Vehículo
    patente = models.CharField(max_length=10)
    ano = models.IntegerField(null=True, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)

    # Inspección
    fecha = models.DateField()
    hora = models.CharField(max_length=10)

    # Pago
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='scanner')
    monto = models.IntegerField(default=0)
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES, default='flow')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    # Control de correos enviados
    confirmacion_enviada = models.BooleanField(default=False)
    recordatorio_enviado = models.BooleanField(default=False)
    followup_enviado = models.BooleanField(default=False)

    # Timestamps
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def get_plan_display_name(self):
        names = {
            'scanner': 'Scanner Automotriz',
            'completa': 'Inspección Completa 360°',
            'promo_2x1': 'Promo 2x1 — Inspección Completa',
        }
        return names.get(self.plan, self.plan.title())

    def get_monto_display(self):
        return f"${self.monto:,.0f}".replace(',', '.')

    def __str__(self):
        return f"{self.orden} — {self.nombre} — {self.patente}"

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-creado_en']
