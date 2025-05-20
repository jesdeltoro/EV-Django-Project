from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Conector(models.Model):
    codigo = models.IntegerField(primary_key=True)
    denominacion = models.CharField(max_length=100)
    potencia_kw = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.denominacion} ({self.potencia_kw} kW)" if self.potencia_kw else self.denominacion

class PuntoRecarga(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=250)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    potencia_kw = models.FloatField(null=True, blank=True)
    tipo_conector = models.ForeignKey(Conector, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if self.tipo_conector and self.tipo_conector.potencia_kw:
            self.potencia_kw = self.tipo_conector.potencia_kw
        else:
            self.potencia_kw = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    punto = models.ForeignKey('PuntoRecarga', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.fecha_expiracion:
            self.fecha_expiracion = self.fecha_inicio + timedelta(minutes=30)
        super().save(*args, **kwargs)

    def is_activa(self):
        return self.fecha_expiracion > timezone.now()







