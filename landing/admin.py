from django.contrib import admin
from .models import Cita, Reserva

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'patente', 'comuna', 'fecha')
    list_filter = ('fecha', 'comuna')
    search_fields = ('nombre', 'patente', 'telefono')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('orden', 'nombre', 'patente', 'plan', 'estado', 'monto', 'creado_en')
    list_filter = ('estado', 'plan', 'fecha')
    search_fields = ('orden', 'nombre', 'patente', 'email')
    readonly_fields = ('orden', 'creado_en', 'actualizado_en')
    fieldsets = (
        ('Identificación', {'fields': ('orden', 'creado_en', 'actualizado_en')}),
        ('Cliente', {'fields': ('nombre', 'email', 'rut', 'telefono')}),
        ('Ubicación', {'fields': ('comuna', 'direccion')}),
        ('Vehículo', {'fields': ('patente', 'ano', 'marca', 'modelo')}),
        ('Inspección', {'fields': ('fecha', 'hora', 'plan', 'monto', 'metodo_pago', 'estado')}),
    )
