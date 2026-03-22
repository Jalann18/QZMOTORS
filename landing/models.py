from django.db import models

class Cita(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    patente = models.CharField(max_length=15)
    comuna = models.CharField(max_length=100)
    fecha = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.patente} - {self.fecha.strftime('%Y-%m-%d')}"
