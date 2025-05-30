from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import stripe
import json
import logging
from django.db import models
from .models import Factura, Pago, MetodoPago, TarifaEnergia
from .services import PaymentService, StripeService
from electrolineras.models import SesionCarga
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class TarifaAPIView(APIView):
    """
    API para obtener la tarifa actual de energía
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        tarifa = TarifaEnergia.get_tarifa_actual()
        return Response({
            'precio_por_kwh': str(tarifa.precio_por_kwh),
            'nombre': tarifa.nombre,
            'currency': 'EUR'
        })


class FacturasUsuarioAPIView(APIView):
    """
    API para obtener las facturas del usuario
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha_creacion')
        
        facturas_data = []
        for factura in facturas:
            facturas_data.append({
                'id': factura.pk,
                'numero_factura': factura.numero_factura,
                'energia_consumida': str(factura.energia_consumida),
                'total': str(factura.total),
                'estado': factura.estado,
                'fecha_creacion': factura.fecha_creacion.isoformat(),
                'fecha_pago': factura.fecha_pago.isoformat() if factura.fecha_pago else None,
                'punto_recarga': factura.sesion_carga.punto_recarga.nombre if factura.sesion_carga else None,
                'puede_pagar': factura.estado == 'pendiente'
            })
        
        return Response(facturas_data)


class CrearPaymentIntentAPIView(APIView):
    """
    API para crear un PaymentIntent para una factura pendiente
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            factura_id = request.data.get('factura_id')
            if not factura_id:
                logger.warning("Solicitud sin ID de factura")
                return Response({'error': 'ID de factura requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que la factura pertenece al usuario y está pendiente
            try:
                factura = Factura.objects.get(
                    id=factura_id,
                    usuario=request.user,
                    estado='pendiente'
                )
            except Factura.DoesNotExist:
                logger.warning(f"Factura no encontrada: ID {factura_id}")
                return Response({'error': 'Factura no encontrada'}, status=status.HTTP_404_NOT_FOUND)
              # Validar monto mínimo antes de crear el PaymentIntent
            if factura.total < Decimal('0.50'):
                logger.warning(f"Factura {factura.pk} tiene un monto de {factura.total} EUR, menor que el mínimo de Stripe (0.50 EUR)")
                # No devolver error, permitir que continúe con el mínimo
            
            # Crear PaymentIntent en Stripe
            try:
                payment_intent = StripeService.crear_payment_intent(
                    cantidad=factura.total,  # Pasar directamente el total en euros
                    metadata={
                        'factura_id': factura.pk,
                        'numero_factura': factura.numero_factura,
                        'usuario_id': request.user.id
                    }
                )
            except Exception as e:
                logger.error(f"Error al crear PaymentIntent en Stripe: {e}")
                return Response({'error': 'Error creando PaymentIntent. Verifica que el monto sea válido.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not payment_intent:
                logger.error("StripeService devolvió None al crear PaymentIntent")
                return Response({'error': 'Error creando PaymentIntent. Por favor intenta nuevamente más tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Actualizar factura con el PaymentIntent
            factura.stripe_payment_intent_id = payment_intent.id
            factura.save()
            logger.info(f"PaymentIntent creado exitosamente para factura {factura_id}")
            
            return Response({
                'client_secret': payment_intent.client_secret,
                'amount': int(factura.total * 100),  # En céntimos
                'currency': 'eur'
            })
            
        except Exception as e:
            logger.error(f"Error creando PaymentIntent: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmarPagoAPIView(APIView):
    """
    API para confirmar que un pago fue exitoso
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            payment_intent_id = request.data.get('payment_intent_id')
            if not payment_intent_id:
                return Response({'error': 'PaymentIntent ID requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar el PaymentIntent en Stripe
            payment_intent = StripeService.obtener_payment_intent(payment_intent_id)
            if not payment_intent:
                return Response({'error': 'PaymentIntent no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
            # Buscar la factura
            try:
                factura = Factura.objects.get(
                    stripe_payment_intent_id=payment_intent_id,
                    usuario=request.user
                )
            except Factura.DoesNotExist:
                return Response({'error': 'Factura no encontrada'}, status=status.HTTP_404_NOT_FOUND)
              # Verificar el estado del pago
            if payment_intent.status == 'succeeded':
                # Pago exitoso
                logger.info(f"Marcando factura {factura.pk} ({factura.numero_factura}) como PAGADA")
                factura.estado = 'pagada'
                factura.fecha_pago = timezone.now()
                factura.save()
                logger.info(f"Estado de factura después de guardar: {factura.estado}")
                
                # Crear registro de pago
                Pago.objects.create(
                    factura=factura,
                    usuario=request.user,
                    cantidad=factura.total,
                    stripe_payment_intent_id=payment_intent_id,
                    stripe_charge_id=payment_intent.latest_charge,
                    estado='exitoso'
                )
                
                return Response({
                    'status': 'success',
                    'mensaje': 'Pago procesado exitosamente',
                    'factura': {
                        'numero_factura': factura.numero_factura,
                        'total': str(factura.total)
                    }
                })
            else:
                return Response({
                    'status': 'failed',
                    'mensaje': 'El pago no fue exitoso'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error confirmando pago: {e}")
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Webhook para manejar eventos de Stripe
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    event = None

    try:
        # Rehabilitar la verificación de firma
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.error("Invalid payload en webhook de Stripe")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except Exception:
        logger.error("Invalid signature en webhook de Stripe")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Manejar el evento
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        try:
            # Buscar la factura asociada
            factura = Factura.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
              # Actualizar estado si no se ha actualizado ya
            logger.info(f"Webhook: Estado actual de factura {factura.pk} ({factura.numero_factura}): {factura.estado}")
            if factura.estado != 'pagada':
                logger.info(f"Webhook: Marcando factura {factura.pk} como PAGADA")
                factura.estado = 'pagada'
                factura.fecha_pago = timezone.now()
                factura.save()
                
                logger.info(f"Webhook: Pago confirmado para factura {factura.numero_factura}. Estado después de guardar: {factura.estado}")
                
        except Factura.DoesNotExist:
            logger.warning(f"Factura no encontrada para PaymentIntent {payment_intent['id']}")
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        
        try:
            factura = Factura.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            
            factura.estado = 'fallida'
            factura.save()
            
            logger.warning(f"Pago fallido por webhook: {factura.numero_factura}")
            
        except Factura.DoesNotExist:
            logger.warning(f"Factura no encontrada para PaymentIntent fallido {payment_intent['id']}")
    
    return JsonResponse({'status': 'success'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def estadisticas_usuario(request):
    """
    API para obtener estadísticas de gastos del usuario
    """
    facturas = Factura.objects.filter(usuario=request.user)
    
    total_gastado = sum(f.total for f in facturas if f.estado == 'pagada')
    total_energia = sum(f.energia_consumida for f in facturas)
    facturas_pendientes = facturas.filter(estado='pendiente').count()
    
    return Response({
        'total_gastado': str(total_gastado),
        'total_energia_consumida': str(total_energia),
        'facturas_pendientes': facturas_pendientes,
        'total_facturas': facturas.count(),
        'precio_promedio_kwh': str(total_gastado / total_energia) if total_energia > 0 else '0'
    })


class PagarFacturaView(TemplateView):
    template_name = 'payments/pagar_factura.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs.get('factura_id')
        factura = get_object_or_404(Factura, id=factura_id)
        user = self.request.user
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['factura_id'] = factura.pk
        context['factura_total'] = factura.total
        context['factura_energia'] = factura.energia_consumida
        context['factura_numero'] = getattr(factura, 'numero_factura', factura.pk)
        # Mostrar formulario solo si el usuario es el dueño y la factura está pendiente
        if user.is_authenticated and factura.usuario == user:
            if factura.estado == 'pendiente':
                context['mostrar_formulario'] = True
            else:
                context['mostrar_formulario'] = False
                context['error_mensaje'] = 'Esta factura ya ha sido pagada o no está pendiente.'
        else:
            context['mostrar_formulario'] = False
            context['error_mensaje'] = 'No tienes permiso para pagar esta factura.'
        return context


class FacturasListView(LoginRequiredMixin, ListView):
    """
    Vista para mostrar la lista de facturas del usuario
    """
    model = Factura
    template_name = 'payments/facturas.html'
    context_object_name = 'facturas'
    paginate_by = 10
    
    def get_queryset(self):
        """Filtrar facturas del usuario actual según el filtro de estado"""
        filtro_estado = self.request.GET.get('estado', None)
        queryset = Factura.objects.filter(usuario=self.request.user)
        
        # Si hay un filtro de estado, aplicarlo
        if filtro_estado and filtro_estado in ['pendiente', 'pagada', 'fallida', 'todas']:
            if filtro_estado != 'todas':
                queryset = queryset.filter(estado=filtro_estado)
        else:
            # Por defecto, mostrar todas las facturas
            queryset = queryset
        
        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenemos todas las facturas del usuario para las estadísticas
        todas_facturas = Factura.objects.filter(usuario=self.request.user)
        context['total_facturas'] = todas_facturas.count()
        context['facturas_pendientes'] = todas_facturas.filter(estado='pendiente').count()
        
        # Añadimos estadísticas para el usuario
        facturas_pagadas = todas_facturas.filter(estado='pagada')
        total_gastado = sum(f.total for f in facturas_pagadas)
        total_energia = sum(f.energia_consumida for f in todas_facturas)
        context['total_gastado'] = total_gastado
        context['total_energia'] = total_energia
        if total_energia > 0:
            context['precio_promedio_kwh'] = total_gastado / total_energia
        else:
            context['precio_promedio_kwh'] = 0
        
        return context
