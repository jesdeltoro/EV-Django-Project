import logging
from decimal import Decimal
from typing import Optional, Union

import stripe
from django.conf import settings
from django.utils import timezone

from .models import Factura, TarifaEnergia

logger = logging.getLogger(__name__)

# Configurar Stripe con la clave secreta
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "sk_test_...")


class StripeService:
    """
    Servicio para encapsular todas las llamadas a la API de Stripe.
    """

    @staticmethod
    def crear_customer(usuario) -> Optional[object]:
        """
        Crea un *Customer* en Stripe para el usuario indicado.
        Devuelve el objeto `stripe.Customer` o `None` si falla.
        """
        try:
            customer = stripe.Customer.create(
                email=usuario.email,
                name=f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username,
                metadata={
                    "user_id": usuario.id,
                    "username": usuario.username,
                },            )
            logger.info(f"✅ Customer creado en Stripe: {customer.id}")
            return customer
        except Exception as exc:
            logger.error("❌ Error creando customer en Stripe: %s", exc)
            return None

    @staticmethod
    def crear_payment_intent(
        cantidad: Union[Decimal, float, str],
        *,
        currency: str = "eur",
        customer_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[stripe.PaymentIntent]:
        """
        Crea un PaymentIntent en Stripe.
        `cantidad` se pasa en euros y se convierte internamente a céntimos.
        """
        try:
            # Convertir cantidad a Decimal para operaciones seguras
            cantidad_decimal = Decimal(str(cantidad))
            
            # Asegurar que la cantidad cumple con el mínimo de Stripe (0.50 EUR)
            if cantidad_decimal < Decimal('0.50'):
                logger.warning(f"⚠️ Cantidad {cantidad_decimal} EUR menor que el mínimo de Stripe (0.50 EUR). Ajustando al mínimo.")
                cantidad_decimal = Decimal('0.50')
            
            intent_data: dict = {
                "amount": int(cantidad_decimal * 100),  # céntimos
                "currency": currency,
                "metadata": metadata or {},
            }

            if customer_id:
                intent_data["customer"] = customer_id

            payment_intent = stripe.PaymentIntent.create(**intent_data)
            logger.info(f"✅ PaymentIntent creado en Stripe: {payment_intent.id}")
            return payment_intent
        except Exception as exc:
            logger.error("❌ Error interactuando con Stripe: %s", exc)
            return None

    @staticmethod
    def confirmar_payment_intent(
        payment_intent_id: str, payment_method_id: str
    ) -> Optional[stripe.PaymentIntent]:
        """
        Confirma un PaymentIntent con un método de pago dado.
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id, payment_method=payment_method_id
            )
            logger.info(f"✅ PaymentIntent confirmado: {payment_intent.id}")
            return payment_intent
        except Exception as exc:
            logger.error("❌ Error confirmando PaymentIntent: %s", exc)
            return None

    @staticmethod
    def obtener_payment_intent(payment_intent_id: str) -> Optional[stripe.PaymentIntent]:
        """
        Recupera un PaymentIntent existente desde Stripe.
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            logger.info(f"✅ PaymentIntent obtenido: {payment_intent.id}")
            return payment_intent
        except Exception as exc:
            logger.error("❌ Error obteniendo PaymentIntent: %s", exc)
            return None


class PaymentService:
    """
    Servicio principal para manejar pagos de sesiones de carga.
    """

    def procesar_sesion_finalizada(self, sesion_carga):
        """
        Procesa el pago al finalizar una sesión de carga.
        Retorna un diccionario con el resultado y la factura generada (si aplica).
        """
        factura = None
        try:
            if sesion_carga.energia_consumida > 0:
                # Obtener la tarifa actual
                tarifa = TarifaEnergia.get_tarifa_actual()
                if not tarifa:
                    raise ValueError("No se pudo obtener la tarifa actual.")

                energia = Decimal(str(sesion_carga.energia_consumida))
                precio = tarifa.precio_por_kwh
                subtotal = energia * precio
                impuestos = subtotal * Decimal('0.21')  # 21% IVA
                total = subtotal + impuestos

                # Fecha de vencimiento a 24 horas
                fecha_vencimiento = timezone.now() + timezone.timedelta(hours=24)

                # Crear la factura
                factura = Factura.objects.create(
                    usuario=sesion_carga.usuario,
                    sesion_carga=sesion_carga,
                    energia_consumida=energia,
                    precio_por_kwh=precio,
                    subtotal=subtotal,
                    impuestos=impuestos,
                    total=total,
                    fecha_vencimiento=fecha_vencimiento
                )
                mensaje = "Factura generada correctamente"
            else:
                mensaje = "No se generó factura porque no hubo consumo"

            return {
                "mensaje": mensaje,
                "factura": factura
            }
        except Exception as exc:
            logger.error(f"❌ Error procesando sesión finalizada: {exc}")
            return {
                "mensaje": "Error procesando sesión finalizada",
                "factura": None
            }
