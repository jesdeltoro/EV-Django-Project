print("Debugging PuntoRecargaSerializer")

from electrolineras.models import PuntoRecarga, Reserva
from electrolineras.serializers import PuntoRecargaSerializer
from django.utils import timezone

# Obtener un punto con reserva activa
punto = PuntoRecarga.objects.get(id=1)
reserva = Reserva.objects.filter(punto=punto, fecha_expiracion__gt=timezone.now()).first()

print(f"Punto ID: {getattr(punto, 'id', 'No id attribute')}")
print(f"Estado del punto: {punto.estado}")
print(f"Reserva activa: {reserva is not None}")
if reserva:
    print(f"Reserva ID: {reserva.pk}")
    print(f"Usuario: {reserva.usuario.username}")
    print(f"Fecha expiración: {reserva.fecha_expiracion}")

# Serializar el punto
serializer = PuntoRecargaSerializer(punto)
data = serializer.data

print("\nSerializado:")
for key, value in data.items():
    print(f"{key}: {value}")

# Comprobar si el campo reserva_id está en el resultado
print(f"\n'reserva_id' en datos?: {'reserva_id' in data}")
print(f"Valor de reserva_id: {data.get('reserva_id')}")
