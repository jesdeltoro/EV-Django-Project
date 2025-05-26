from django.db import models
from django.contrib.auth import get_user_model
from electrolineras.models import SesionCarga
from decimal import Decimal

User = get_user_model()

class TarifaEnergia(models.Model):
    """
    Modelo para gestionar las tarifas de energía por kWh
    """
    id = models.AutoField(primary_key=True)  # Definir explícitamente el campo id
    nombre = models.CharField(max_length=100, help_text="Nombre de la tarifa")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción de la tarifa")
    precio_por_kwh = models.DecimalField(
        max_digits=6, 
        decimal_places=3, 
        help_text="Precio por kWh en euros"
    )
    activa = models.BooleanField(default=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True, help_text="Fecha de inicio de la tarifa")  # Nuevo campo
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True, help_text="Fecha de finalización de la tarifa")

    class Meta:
        verbose_name = "Tarifa de Energía"
        verbose_name_plural = "Tarifas de Energía"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.precio_por_kwh}€/kWh"
    
    @classmethod
    def get_tarifa_actual(cls):
        """Obtiene la tarifa activa actual"""
        tarifa = cls.objects.filter(activa=True).first()
        if not tarifa:
            # Crear tarifa por defecto si no existe ninguna
            tarifa = cls.objects.create(
                nombre="Tarifa Standard",
                precio_por_kwh=Decimal('0.30'),  # 30 céntimos por kWh
                activa=True
            )
        return tarifa


class MetodoPago(models.Model):
    """
    Almacena los métodos de pago de los usuarios
    """
    TIPO_CHOICES = [
        ('card', 'Tarjeta de Crédito'),
        ('paypal', 'PayPal'),
        ('bank', 'Transferencia Bancaria'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metodos_pago')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='card')
    stripe_payment_method_id = models.CharField(max_length=100, blank=True, null=True)
    ultimos_4_digitos = models.CharField(max_length=4, blank=True, null=True)
    marca_tarjeta = models.CharField(max_length=20, blank=True, null=True)  # visa, mastercard, etc.
    activo = models.BooleanField(default=True)
    es_predeterminado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['-es_predeterminado', '-fecha_creacion']
    
    def __str__(self):
        if self.ultimos_4_digitos:
            return f"{self.get_tipo_display()} **** {self.ultimos_4_digitos}"
        return f"{self.get_tipo_display()} - {self.usuario.username}"

    def get_tipo_display(self):
        """Devuelve la representación legible del tipo de método de pago"""
        return dict(self.TIPO_CHOICES).get(self.tipo, self.tipo)


class Factura(models.Model):
    """
    Representa una factura generada por una sesión de carga
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('fallida', 'Fallida'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facturas')
    sesion_carga = models.OneToOneField(
        SesionCarga, 
        on_delete=models.CASCADE, 
        related_name='factura'
    )
    numero_factura = models.CharField(max_length=20, unique=True)
    
    # Datos de energía
    energia_consumida = models.DecimalField(max_digits=8, decimal_places=3)  # kWh
    precio_por_kwh = models.DecimalField(max_digits=6, decimal_places=3)     # €/kWh
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)           # €
    impuestos = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))  # €
    total = models.DecimalField(max_digits=8, decimal_places=2)              # €
    
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField()
    fecha_pago = models.DateTimeField(blank=True, null=True)
    
    # Datos de Stripe
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    metodo_pago_usado = models.ForeignKey(
        MetodoPago, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Factura {self.numero_factura} - {self.usuario.username}"
    
    def save(self, *args, **kwargs):
        if not self.numero_factura:
            self.generar_numero_factura()
        super().save(*args, **kwargs)
    
    def generar_numero_factura(self):
        """Genera un número de factura único"""
        from django.utils import timezone
        import random
        
        fecha = timezone.now()
        base = f"EV{fecha.year}{fecha.month:02d}{fecha.day:02d}"
        
        # Buscar el último número para evitar duplicados
        ultima_factura = Factura.objects.filter(
            numero_factura__startswith=base
        ).order_by('-numero_factura').first()
        
        if ultima_factura:
            try:
                ultimo_numero = int(ultima_factura.numero_factura[-4:])
                nuevo_numero = ultimo_numero + 1
            except ValueError:
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        self.numero_factura = f"{base}{nuevo_numero:04d}"
    
    def calcular_total(self):
        """Calcula el total de la factura incluyendo impuestos"""
        self.subtotal = self.energia_consumida * self.precio_por_kwh
        # IVA del 21% en España
        self.impuestos = self.subtotal * Decimal('0.21')
        self.total = self.subtotal + self.impuestos
        return self.total


class Pago(models.Model):
    """
    Registro de pagos realizados
    """
    ESTADO_CHOICES = [
        ('procesando', 'Procesando'),
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    cantidad = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='procesando')
    
    # Datos de Stripe
    stripe_payment_intent_id = models.CharField(max_length=100)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Información adicional
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pago {self.pk} - {self.cantidad}€ - {dict(self.ESTADO_CHOICES).get(self.estado, self.estado)}"
