#!/usr/bin/env python
"""
Script para verificar y corregir el estado de las facturas basado en los pagos registrados.
Este script comprueba si hay pagos exitosos para facturas que están marcadas como pendientes,
y las marca como pagadas si corresponde.

Ejecutar: python corregir_facturas.py
"""
import os
import django
import logging
from django.utils import timezone

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrolineras_project.settings')
django.setup()

from payments.models import Factura, Pago

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def corregir_estados_facturas():
    """Corrige el estado de las facturas basado en los pagos registrados"""
    # Obtener todas las facturas pendientes
    facturas_pendientes = Factura.objects.filter(estado='pendiente')
    logger.info(f"Facturas pendientes encontradas: {facturas_pendientes.count()}")
    
    facturas_actualizadas = 0
    
    for factura in facturas_pendientes:
        # Buscar pagos exitosos para esta factura
        pagos_exitosos = Pago.objects.filter(factura=factura, estado='exitoso')
        
        if pagos_exitosos.exists():
            # Si hay pagos exitosos, marcar la factura como pagada
            logger.info(f"Factura {factura.pk} ({factura.numero_factura}) tiene pagos exitosos pero está marcada como pendiente")
            factura.estado = 'pagada'
            primer_pago = pagos_exitosos.first()
            if primer_pago is not None and hasattr(primer_pago, 'fecha_creacion'):
                factura.fecha_pago = primer_pago.fecha_creacion
            else:
                factura.fecha_pago = timezone.now()
            factura.save()
            facturas_actualizadas += 1
            logger.info(f"Factura {factura.numero_factura} actualizada a PAGADA")
    
    logger.info(f"Total facturas actualizadas: {facturas_actualizadas}")
    
    # Verificar facturas pagadas sin pagos asociados
    facturas_pagadas = Factura.objects.filter(estado='pagada')
    for factura in facturas_pagadas:
        if not Pago.objects.filter(factura=factura, estado='exitoso').exists():
            logger.warning(f"ANOMALÍA: Factura {factura.numero_factura} marcada como PAGADA pero no tiene pagos exitosos")
    
    # Resumen final
    facturas_pendientes = Factura.objects.filter(estado='pendiente').count()
    facturas_pagadas = Factura.objects.filter(estado='pagada').count() 
    facturas_total = Factura.objects.all().count()
    
    logger.info(f"RESUMEN: Pendientes={facturas_pendientes}, Pagadas={facturas_pagadas}, Total={facturas_total}")


def verificar_pagos_stripe():
    """Verifica los payment intents en Stripe para facturas pendientes con stripe_payment_intent_id"""
    try:
        import stripe
        from django.conf import settings
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        facturas_con_intent = Factura.objects.filter(
            estado='pendiente', 
            stripe_payment_intent_id__isnull=False
        )
        
        logger.info(f"Verificando {facturas_con_intent.count()} facturas con PaymentIntent")
        
        for factura in facturas_con_intent:
            try:
                if factura.stripe_payment_intent_id is not None:
                    payment_intent = stripe.PaymentIntent.retrieve(factura.stripe_payment_intent_id)
                    
                    if payment_intent.status == 'succeeded':
                        logger.info(f"PaymentIntent {payment_intent.id} está succeeded pero factura {factura.numero_factura} está pendiente")
                        factura.estado = 'pagada'
                        factura.fecha_pago = timezone.now()
                        factura.save()
                        logger.info(f"Factura {factura.numero_factura} actualizada a PAGADA basado en PaymentIntent")
                        
                        # Crear registro de pago si no existe
                        if not Pago.objects.filter(stripe_payment_intent_id=payment_intent.id).exists():
                            Pago.objects.create(
                                factura=factura,
                                usuario=factura.usuario,
                                cantidad=factura.total,
                                stripe_payment_intent_id=payment_intent.id,
                                stripe_charge_id=getattr(payment_intent, 'latest_charge', None),
                                estado='exitoso'
                            )
                            logger.info(f"Registro de pago creado para factura {factura.numero_factura}")
                else:
                    logger.warning(f"Factura {factura.numero_factura} no tiene stripe_payment_intent_id")
            
            except Exception as e:
                logger.error(f"Error verificando PaymentIntent para factura {factura.numero_factura}: {e}")
    
    except ImportError:
        logger.error("No se pudo importar stripe")
    except Exception as e:
        logger.error(f"Error general verificando pagos en Stripe: {e}")


if __name__ == "__main__":
    logger.info("Iniciando verificación y corrección de estados de facturas")
    corregir_estados_facturas()
    verificar_pagos_stripe()
    logger.info("Proceso completado")
