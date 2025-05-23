from electrolineras.models import PuntoRecarga, Reserva
from django.utils import timezone

# Verificar punto con ID 1
punto = PuntoRecarga.objects.get(id=1)
print(f'Punto ID: {punto.pk}, Estado: {punto.estado}')

# Verificar si hay reservas activas para este punto
reserva = Reserva.objects.filter(punto=punto, fecha_expiracion__gt=timezone.now()).first()
print(f'Reserva activa: {reserva is not None}')
if reserva:
    print(f'Reserva ID: {reserva.pk}, Usuario: {reserva.usuario.username}, Expira: {reserva.fecha_expiracion}')

# Verificar condiciones para mostrar el botón "Iniciar carga"
print("\nCondiciones para mostrar el botón:")
print(f'1. Estado == "reservado": {punto.estado == "reservado"}')
if reserva:
    usuario_actual = reserva.usuario.username
    print(f'2. Usuario de reserva: {usuario_actual}')
    print(f'3. reserva_id existe: {reserva.pk is not None}')
    print(f'\nResumen: Mostrará botón si usuario es {usuario_actual} y el estado es "reservado"')
