from electrolineras.models import PuntoRecarga, Reserva
from django.utils import timezone
from django_types import with_id

# Identificar puntos con reservas activas
print('Verificando puntos con reservas activas:')
reservas_activas = Reserva.objects.filter(fecha_expiracion__gt=timezone.now())
for reserva in reservas_activas:
    punto = reserva.punto
    punto_with_id = with_id(punto)
    print(f'Reserva ID: {reserva.pk}, Punto: {punto_with_id.id}, Nombre: "{punto.nombre}", Estado: {punto.estado}')
    
    # Verificar si el estado es incorrecto y corregirlo
    if punto.estado != 'reservado':
        print(f'   ⚠️ Estado incorrecto. Actualizando de "{punto.estado}" a "reservado"')
        punto.estado = 'reservado'
        punto.save()
    else:
        print('   ✅ Estado correcto')

# Buscar si hay más puntos que deberían tener reservas pero no las tienen
print('\nVerificando puntos marcados como reservados:')
puntos_reservados = PuntoRecarga.objects.filter(estado='reservado')
for punto in puntos_reservados:
    tiene_reserva = Reserva.objects.filter(punto=punto, fecha_expiracion__gt=timezone.now()).exists()
    if tiene_reserva:
        print(f'Punto ID: {punto.pk}, Nombre: "{punto.nombre}" ✅ - Correctamente reservado')
    else:
        print(f'Punto ID: {punto.pk}, Nombre: "{punto.nombre}" ⚠️ - Marcado como reservado pero sin reserva activa')
        print(f'   Actualizando estado a "disponible"')
        punto.estado = 'disponible'
        punto.save()
