from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from datetime import datetime
from .models import Cita
from .flow_api import create_payment, get_payment_status

# Flow Integration Ready
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

@csrf_exempt
def checkout_process(request):
    """Recibe los datos del checkout frontend e inicia el pago con Flow"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan = data.get('plan', 'scanner')
            metodo = data.get('payment_method', 'flow')
            
            prices = {'scanner': 30000, 'completa': 65000, 'promo_2x1': 100000}
            amount = prices.get(plan, 30000)
            
            # Si eligió pago presencial, no llamamos a Flow
            if metodo == 'presencial':
                return JsonResponse({"success": True, "presencial": True})
            
            orden_str = str(uuid.uuid4()).replace("-", "")
            orden_compra = f"QZ-{plan.upper()}-{orden_str[:6].upper()}"
            
            url_return = request.build_absolute_uri('/checkout/return/')
            url_confirm = request.build_absolute_uri('/checkout/confirm/')
            
            flow_response = create_payment(
                commerce_order=orden_compra,
                subject=f"Inspección QZ Motors: {plan.title()}",
                amount=amount,
                email=data.get('email', 'cliente@correo.cl'),
                return_url=url_return,
                confirm_url=url_confirm
            )
            
            if flow_response.get('success'):
                return JsonResponse({"success": True, "redirect_url": flow_response['url']})
            else:
                return JsonResponse({"success": False, "error": flow_response.get('error')})
                
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
            
    return JsonResponse({"success": False, "error": "Invalid Method"})

@csrf_exempt
def checkout_return(request):
    """Página donde el usuario aterriza luego de pagar/cancelar en Flow"""
    token = request.POST.get('token') or request.GET.get('token')
    
    if not token:
        return render(request, 'landing/checkout_return.html', {'status': 'error', 'message': 'Token no encontrado'})
        
    status_data = get_payment_status(token)
    full_order = status_data.get('commerceOrder', '')
    
    # Extract plan_id from QZ-PLANNAME-RANDOM
    parts = full_order.split('-')
    plan_id = parts[1].lower() if len(parts) > 2 else 'promo_2x1'
    
    if status_data.get('status') == 2: # Pagado
        context = {
            'status': 'success', 
            'order': full_order, 
            'amount': status_data.get('amount'),
            'plan': plan_id
        }
    else:
        context = {
            'status': 'failed', 
            'order': full_order or 'Desconocida',
            'plan': plan_id
        }
        
    return render(request, 'landing/checkout_return.html', context)

@csrf_exempt
def checkout_confirm(request):
    """Webhook oculto que Flow llama de servidor a servidor para confirmar el pago seguro"""
    token = request.POST.get('token')
    if not token:
        return HttpResponse("Token no provisto", status=400)
        
    status_data = get_payment_status(token)
    if status_data.get('status') == 2:
        return HttpResponse("OK", status=200)
        
    return HttpResponse("Pago no completado", status=400)
