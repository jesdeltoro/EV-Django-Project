#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrolineras_project.settings')
django.setup()

from electrolineras.models import PuntoRecarga, Conector

print('=== PUNTOS DE RECARGA ===')
for punto in PuntoRecarga.objects.all()[:5]:
    print(f'Nombre: {punto.nombre}')
    print(f'Dirección: {punto.direccion}')
    print(f'Potencia: {punto.potencia_kw} kW')
    print(f'Estado: {getattr(punto, "estado", "sin estado")}')
    print(f'Conector: {punto.tipo_conector.denominacion if punto.tipo_conector else "Sin conector"}')
    print('---')

print('=== CONECTORES ===')
for conector in Conector.objects.all():
    print(f'{conector.codigo}: {conector.denominacion} - {conector.potencia_kw} kW')

print(f'Total puntos: {PuntoRecarga.objects.count()}')
print(f'Total conectores: {Conector.objects.count()}')
