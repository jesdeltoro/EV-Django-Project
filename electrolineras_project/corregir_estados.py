from electrolineras.models import PuntoRecarga, Reserva
from django.utils import timezone

# Obtener puntos con reservas activas pero estado incorrecto
reservas_activas = Reserva.objects.filter(fecha_expiracion__gt=timezone.now())
for reserva in reservas_activas:
    punto = reserva.punto
    if punto.estado != 'reservado':
        print(f"Corrigiendo punto {punto.id} '{punto.nombre}' - Estado actual: {punto.estado}")
        punto.estado = 'reservado'
        punto.save()
        print(f"  → Estado actualizado a: {punto.estado}")
    else:
        print(f"Punto {punto.id} '{punto.nombre}' ya está en estado correcto: {punto.estado}")
