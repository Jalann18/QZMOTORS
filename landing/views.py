from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import logging
from datetime import datetime
from .models import Cita, Reserva
from .flow_api import create_payment, get_payment_status
from .emails import send_confirmation_email, send_admin_notification

# Configuración de Logging
logger = logging.getLogger(__name__)


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
    prices = {'scanner': 350, 'completa': 65000, 'promo_2x1': 100000}

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
        monto=prices.get(plan, 350),
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
            prices = {'scanner': 30000, 'completa': 65000, 'promo_2x1': 100000}
            amount = prices.get(plan, 30000)

            # Log inicio
            logger.info(f"[CHECKOUT START] Plan: {plan}, Metodo: {metodo}, Email: {data.get('email')}")

            orden = _build_orden(plan)

            # ── Pago presencial ──
            if metodo == 'presencial':
                reserva = _save_reserva(data, orden, estado='confirmada')
                send_confirmation_email(reserva)   # Correo al cliente
                send_admin_notification(reserva)   # Correo al admin (QZ Motors)
                return JsonResponse({"success": True, "presencial": True})

            # ── Pago Flow ──
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
                logger.info(f"[CHECKOUT FLOW OK] Orden {orden} redirigiendo a {flow_response['url']}")
                return JsonResponse({"success": True, "redirect_url": flow_response['url']})
            else:
                logger.error(f"[CHECKOUT FLOW ERROR] Error en Flow: {flow_response.get('error')}")
                Reserva.objects.filter(orden=orden).delete()
                return JsonResponse({"success": False, "error": flow_response.get('error')})

        except Exception as e:
            logger.exception(f"[CHECKOUT CRASH] Error inesperado en checkout_process: {e}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid Method"})


@csrf_exempt
def checkout_return(request):
    """Página donde el usuario aterriza luego de pagar/cancelar en Flow."""
    token = request.POST.get('token') or request.GET.get('token')
    logger.info(f"[CHECKOUT RETURN] Recibido retorno con token: {token}")

    if not token:
        logger.warning("[CHECKOUT RETURN] No se encontró token en el request")
        return render(request, 'landing/checkout_return.html', {
            'status': 'error',
            'message': 'Token no encontrado'
        })

    status_data = get_payment_status(token)
    full_order = status_data.get('commerceOrder')
    
    # Validar que full_order exista para evitar errores de split()
    if not full_order:
        logger.error(f"[CHECKOUT RETURN ERROR] Flow no devolvió commerceOrder. Respuesta cruda: {status_data}")
        return render(request, 'landing/checkout_return.html', {
            'status': 'failed',
            'order': 'Desconocida',
            'message': 'No se pudo identificar la orden en la respuesta de Flow.'
        })

    # Parsing seguro del plan desde la orden
    parts = full_order.split('-')
    plan_id = parts[1].lower() if len(parts) > 1 else 'promo_2x1'

    if status_data.get('status') == 2:  # Pagado exitosamente
        logger.info(f"[CHECKOUT SUCCESS] Pago confirmado para orden {full_order}")
        try:
            reserva = Reserva.objects.get(orden=full_order)
            if reserva.estado != 'confirmada':
                reserva.estado = 'confirmada'
                reserva.save(update_fields=['estado'])
                send_confirmation_email(reserva)   # Correo al cliente
                send_admin_notification(reserva)   # Correo al admin (QZ Motors)
        except Reserva.DoesNotExist:
            logger.error(f"[CHECKOUT ERROR] Reserva {full_order} no encontrada en DB tras pago exitoso.")
        except Exception as e:
            logger.exception(f"[CHECKOUT ERROR] Error al actualizar reserva {full_order}: {e}")

        context = {
            'status': 'success',
            'order': full_order,
            'amount': status_data.get('amount'),
            'plan': plan_id
        }
    else:
        logger.warning(f"[CHECKOUT FAILED] Pago fallido o cancelado para orden {full_order}. Status: {status_data.get('status')}")
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
