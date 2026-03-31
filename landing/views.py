from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from datetime import datetime
from .models import Cita, Reserva
from .flow_api import create_payment, get_payment_status
from .emails import send_confirmation_email


# ──────────────────────────────────────────────
# Páginas principales
# ──────────────────────────────────────────────

def index(request):
    return render(request, 'landing/index.html')


def checkout(request):
    return render(request, 'landing/checkout.html')


# ──────────────────────────────────────────────
# API heredada (mantenida por compatibilidad)
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _build_orden(plan):
    uid = str(uuid.uuid4()).replace("-", "")
    return f"QZ-{plan.upper()}-{uid[:6].upper()}"


def _save_reserva(data, orden, estado='pendiente'):
    """Crea o actualiza una Reserva con los datos del checkout."""
    plan = data.get('plan', 'scanner')
    prices = {'scanner': 1, 'completa': 65000, 'promo_2x1': 100000}

    fecha_str = data.get('fecha', '')
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = datetime.today().date()

    reserva = Reserva.objects.create(
        orden=orden,
        nombre=data.get('nombre', ''),
        email=data.get('email', ''),
        rut=data.get('rut', ''),
        telefono=data.get('telefono', ''),
        comuna=data.get('comuna', ''),
        direccion=data.get('direccion', ''),
        patente=data.get('patente', '').upper(),
        ano=data.get('ano') or None,
        marca=data.get('marca', ''),
        modelo=data.get('modelo', ''),
        fecha=fecha,
        hora=data.get('hora', ''),
        plan=plan,
        monto=prices.get(plan, 1),
        metodo_pago=data.get('payment_method', 'flow'),
        estado=estado,
    )
    return reserva


# ──────────────────────────────────────────────
# Checkout
# ──────────────────────────────────────────────

@csrf_exempt
def checkout_process(request):
    """Recibe los datos del checkout frontend e inicia el pago con Flow."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan = data.get('plan', 'scanner')
            metodo = data.get('payment_method', 'flow')
            prices = {'scanner': 1, 'completa': 65000, 'promo_2x1': 100000}
            amount = prices.get(plan, 1)

            orden = _build_orden(plan)

            # ── Pago presencial ──
            if metodo == 'presencial':
                reserva = _save_reserva(data, orden, estado='confirmada')
                send_confirmation_email(reserva)  # Correo #1 inmediato
                return JsonResponse({"success": True, "presencial": True})

            # ── Pago Flow ──
            # Guardamos pendiente antes de redirigir; se confirma en checkout_return
            _save_reserva(data, orden, estado='pendiente')

            url_return = request.build_absolute_uri('/checkout/return/')
            url_confirm = request.build_absolute_uri('/checkout/confirm/')

            flow_response = create_payment(
                commerce_order=orden,
                subject=f"Inspección QZ Motors: {plan.title()}",
                amount=amount,
                email=data.get('email', 'cliente@correo.cl'),
                return_url=url_return,
                confirm_url=url_confirm
            )

            if flow_response.get('success'):
                return JsonResponse({"success": True, "redirect_url": flow_response['url']})
            else:
                # Limpiar reserva pendiente si Flow falla
                Reserva.objects.filter(orden=orden).delete()
                return JsonResponse({"success": False, "error": flow_response.get('error')})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid Method"})


@csrf_exempt
def checkout_return(request):
    """Página donde el usuario aterriza luego de pagar/cancelar en Flow."""
    token = request.POST.get('token') or request.GET.get('token')

    if not token:
        return render(request, 'landing/checkout_return.html', {
            'status': 'error',
            'message': 'Token no encontrado'
        })

    status_data = get_payment_status(token)
    full_order = status_data.get('commerceOrder', '')

    parts = full_order.split('-')
    plan_id = parts[1].lower() if len(parts) > 2 else 'promo_2x1'

    if status_data.get('status') == 2:  # Pagado exitosamente
        # Confirmar la reserva y enviar correo #1
        try:
            reserva = Reserva.objects.get(orden=full_order)
            reserva.estado = 'confirmada'
            reserva.save(update_fields=['estado'])
            send_confirmation_email(reserva)  # Correo #1
        except Reserva.DoesNotExist:
            pass  # La reserva puede no existir si hubo un error previo

        context = {
            'status': 'success',
            'order': full_order,
            'amount': status_data.get('amount'),
            'plan': plan_id
        }
    else:
        # Marcar como cancelada
        Reserva.objects.filter(orden=full_order).update(estado='cancelada')
        context = {
            'status': 'failed',
            'order': full_order or 'Desconocida',
            'plan': plan_id
        }

    return render(request, 'landing/checkout_return.html', context)


@csrf_exempt
def checkout_confirm(request):
    """Webhook oculto que Flow llama de servidor a servidor para confirmar el pago."""
    token = request.POST.get('token')
    if not token:
        return HttpResponse("Token no provisto", status=400)

    status_data = get_payment_status(token)
    if status_data.get('status') == 2:
        full_order = status_data.get('commerceOrder', '')
        Reserva.objects.filter(orden=full_order).update(estado='confirmada')
        return HttpResponse("OK", status=200)

    return HttpResponse("Pago no completado", status=400)
