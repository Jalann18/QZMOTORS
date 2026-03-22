from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'patente', 'comuna', 'fecha')
    list_filter = ('fecha', 'comuna')
    search_fields = ('nombre', 'patente', 'telefono')
