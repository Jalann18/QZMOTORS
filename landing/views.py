from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cita
from datetime import datetime

def index(request):
    return render(request, 'landing/index.html')

def checkout(request):
    return render(request, 'landing/checkout.html')

@csrf_exempt
def agendar_cita(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            telefono = data.get('telefono')
            patente = data.get('patente')
            comuna = data.get('comuna')
            fecha_str = data.get('fecha')
            
            # Basic validation
            if not all([nombre, telefono, patente, comuna, fecha_str]):
                return JsonResponse({'success': False, 'error': 'Faltan campos requeridos'})
                
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            Cita.objects.create(
                nombre=nombre,
                telefono=telefono,
                patente=patente,
                comuna=comuna,
                fecha=fecha
            )
            
            return JsonResponse({'success': True, 'message': 'Cita agendada con éxito'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
