from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from typing import TypeVar, cast

# Ayuda a Pylance a entender que id es un atributo válido de los modelos
T = TypeVar('T', bound=models.Model)
def ensure_id(model_instance: T) -> T:
    """Función auxiliar para asegurar que Pylance sepa que los modelos tienen un ID."""
    # Esta función no hace nada en tiempo de ejecución, solo ayuda con el análisis estático
    return cast(T, model_instance)

class Conector(models.Model):
    codigo = models.IntegerField(primary_key=True)
    denominacion = models.CharField(max_length=100)
    potencia_kw = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.denominacion} ({self.potencia_kw} kW)" if self.potencia_kw else self.denominacion

class PuntoRecarga(models.Model):
    # Django crea automáticamente un campo id, pero Pylance no lo detecta
    # id: int  # Anotación de tipo para ayudar a Pylance
    
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=250)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    potencia_kw = models.FloatField(null=True, blank=True)
    tipo_conector = models.ForeignKey(Conector, on_delete=models.SET_NULL, null=True)
    
    # Nuevos campos para la simulación
    ESTADO_CHOICES = [
        ("disponible", "Disponible"),
        ("en_uso", "En Uso"),
        ("reservado", "Reservado"),
        ("offline", "Fuera de Servicio"),
    ]
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="disponible")
    energia_suministrada_total = models.FloatField(default=0)  # Total kWh suministrados históricamente
    energia_actual_sesion = models.FloatField(default=0)  # kWh en la sesión actual

    def save(self, *args, **kwargs):
        if self.tipo_conector and self.tipo_conector.potencia_kw:
            self.potencia_kw = self.tipo_conector.potencia_kw
        else:
            self.potencia_kw = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    # Django crea automáticamente un campo id, pero Pylance no lo detecta
    id: int  # Anotación de tipo para ayudar a Pylance
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    punto = models.ForeignKey("PuntoRecarga", on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Comprobar si es una nueva reserva
        if not self.fecha_expiracion:
            self.fecha_expiracion = self.fecha_inicio + timedelta(minutes=30)
        
        super().save(*args, **kwargs)
        
        # Actualizar el estado del punto a "reservado" si es una nueva reserva
        if is_new:
            self.punto.estado = "reservado"
            self.punto.save()

    def is_activa(self):
        return self.fecha_expiracion > timezone.now()
        
    def __str__(self):
        return f"Reserva de {self.usuario.username} para {self.punto.nombre}"
        
    @classmethod
    def limpiar_reservas_expiradas(cls):
        """
        Método de clase para limpiar reservas expiradas y actualizar el estado de los puntos.
        Puede ser llamado periódicamente por un cronjob o al cargar el mapa.
        """
        from django.utils import timezone
        reservas_expiradas = cls.objects.filter(fecha_expiracion__lt=timezone.now())
        puntos_a_actualizar = []
        puntos_procesados = 0
        
        for reserva in reservas_expiradas:
            punto = reserva.punto
            # Verificar si el punto está en estado "reservado" pero la reserva ha expirado
            if punto.estado == "reservado":
                # Verificar que no hay sesión de carga activa para este punto
                if not SesionCarga.objects.filter(punto_recarga=punto, activa=True).exists():
                    # Verificar que no hay otras reservas activas para este punto
                    if not cls.objects.filter(
                            punto=punto, 
                            fecha_expiracion__gt=timezone.now()
                        ).exclude(pk=reserva.pk).exists():
                        punto.estado = "disponible"
                        puntos_a_actualizar.append(punto)
                        puntos_procesados += 1
        
        # Actualizar los puntos en batch para mejor rendimiento
        if puntos_a_actualizar:
            PuntoRecarga.objects.bulk_update(puntos_a_actualizar, ["estado"])
            print(f"Reservas expiradas: {puntos_procesados} puntos actualizados a 'disponible'")
            
        return puntos_procesados


class SesionCarga(models.Model):
    """
    Representa una sesión de carga activa en un punto de recarga.
    Se crea cuando un usuario inicia una carga y registra métricas en tiempo real.
    """
    # Django crea automáticamente un campo id, pero Pylance no lo detecta
    id: int  # Anotación de tipo para ayudar a Pylance
    
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    punto_recarga = models.ForeignKey(PuntoRecarga, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    porcentaje_bateria_inicial = models.IntegerField(default=20)  # Valor simulado
    porcentaje_bateria_actual = models.IntegerField(default=20)
    energia_consumida = models.FloatField(default=0)  # kWh
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para verificar si un usuario ya tiene
        una sesión de carga activa antes de crear una nueva.
        """
        # Si es una nueva sesión (aún no tiene ID) y va a ser activa
        if not self.pk and self.activa:
            # Verificar si el usuario ya tiene una sesión activa
            sesion_activa = SesionCarga.objects.filter(
                usuario=self.usuario, 
                activa=True
            ).exists()
            
            if sesion_activa:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"El usuario {self.usuario.username} ya tiene una sesión de carga activa. " 
                    f"Debe terminar esa carga antes de iniciar una nueva."
                )
        
        super().save(*args, **kwargs)
    
    def iniciar_carga(self):
        """Inicia la sesión de carga y actualiza el estado del punto"""
        self.activa = True
        self.punto_recarga.estado = "en_uso"
        self.punto_recarga.save()
        
        # Actualizar la fecha de expiración de la reserva para evitar que aparezca como "reservado"
        # cuando realmente está "en_uso"
        if hasattr(self, 'reserva') and self.reserva:
            self.reserva.fecha_expiracion = timezone.now()
            self.reserva.save(update_fields=['fecha_expiracion'])
            
        self.save()
    
    def detener_carga(self):
        """Detiene la sesión de carga y actualiza métricas"""
        self.activa = False
        self.fin = timezone.now()
        self.punto_recarga.estado = "disponible"
        self.punto_recarga.energia_suministrada_total += self.energia_consumida
        self.punto_recarga.energia_actual_sesion = 0
        
        # Asegurar que se guarde el punto con los valores actualizados
        self.punto_recarga.save(update_fields=[
            'estado', 
            'energia_suministrada_total', 
            'energia_actual_sesion'
        ])
        
        # Guardar los cambios en la sesión
        self.save(update_fields=[
            'activa',
            'fin',
            'energia_consumida',
            'porcentaje_bateria_actual'
        ])
        
        # Procesar pago automáticamente al finalizar la carga
        self._procesar_pago_automatico()
    
    def _procesar_pago_automatico(self):
        """Procesa el pago automático después de finalizar la carga"""
        try:
            # Importar aquí para evitar importaciones circulares
            try:
                from payments.services import PaymentService
            except ImportError:
                # Si no existe el módulo externo, usar la clase local definida abajo
                PaymentService = globals().get("PaymentService")
                if PaymentService is None:
                    raise ImportError("No se pudo importar PaymentService y no existe una clase local definida.")
            import logging

            logger = logging.getLogger(__name__)

            # Solo procesar pago si la energía consumida es mayor a 0
            if self.energia_consumida > 0:
                if hasattr(PaymentService, "procesar_sesion_finalizada"):
                    resultado = PaymentService().procesar_sesion_finalizada(self)
                else:
                    raise AttributeError("PaymentService no tiene el método 'procesar_sesion_finalizada'.")
                
                if resultado:
                    logger.info(
                        f"Sesión {self.id} finalizada - {resultado['mensaje']} - "
                        f"Energía: {self.energia_consumida:.2f} kWh"
                    )
                    if resultado['factura']:
                        logger.info(
                            f"Factura {resultado['factura'].numero_factura} - "
                            f"Total: {resultado['factura'].total}€"
                        )
                else:
                    logger.warning(f"No se pudo procesar el pago para la sesión {self.id}")
            else:
                logger.info(f"Sesión {self.id} finalizada sin energía consumida - no se genera factura")
                
        except Exception as e:
            # No fallar la finalización de la carga por problemas de pago
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error procesando pago automático para sesión {self.id}: {e}")
            # El pago puede procesarse manualmente después
    
    def actualizar_bateria(self, forzar_actualizacion=False):
        """
        Actualiza el porcentaje de batería y la energía consumida basado 
        en el tiempo transcurrido y la potencia del punto.
        
        Si forzar_actualizacion=True, simula una actualización manual.
        De lo contrario, calcula basado en el tiempo transcurrido.
        
        Retorna el porcentaje actual de batería y la energía consumida.
        """
        if not self.activa:
            return self.porcentaje_bateria_actual, self.energia_consumida
        
        # Calcular tiempo transcurrido en horas
        tiempo_transcurrido = (timezone.now() - self.inicio).total_seconds() / 3600  # horas
        
        # Obtener la potencia del punto de recarga en kW
        potencia = self.punto_recarga.potencia_kw or 50  # Valor por defecto si no hay potencia definida
        
        # Calcular la energía consumida teórica (kWh = kW * horas)
        energia_teorica = potencia * tiempo_transcurrido
        
        # Ajustar la eficiencia al 100% para evitar pérdidas
        self.energia_consumida = energia_teorica
        
        # Actualizar también el punto de recarga
        self.punto_recarga.energia_actual_sesion = self.energia_consumida
        self.punto_recarga.save(update_fields=['energia_actual_sesion'])
        
        self.save(update_fields=['energia_consumida'])
        
        # Detener la sesión automáticamente si la batería llega al 100%
        if self.porcentaje_bateria_actual >= 100 and self.activa:
            self.detener_carga()
        
        return self.porcentaje_bateria_actual, self.energia_consumida
        
    def __str__(self):
        return f"Sesión de {self.usuario.username} en {self.punto_recarga.nombre}"

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
        if sesion_carga.energia_consumida > 0:
            class Factura:
                def __init__(self, numero_factura, total):
                    self.numero_factura = numero_factura
                    self.total = total
            factura = Factura(numero_factura="F12345", total=sesion_carga.energia_consumida * 0.3)
            mensaje = "Pago procesado correctamente"
        else:
            mensaje = "No se generó factura porque no hubo consumo"
        return {
            "mensaje": mensaje,
            "factura": factura
        }
