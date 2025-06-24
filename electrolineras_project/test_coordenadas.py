#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrolineras_project.settings')
django.setup()

from electrolineras.models import PuntoRecarga

def test_coordenadas():
    print("=== VERIFICACIÓN DE COORDENADAS EN LA BASE DE DATOS ===")
    
    puntos = PuntoRecarga.objects.all()
    print(f"\nTotal de puntos de recarga: {puntos.count()}")
    
    for punto in puntos:
        print(f"\n📍 {punto.nombre}")
        print(f"   Dirección: {punto.direccion}")
        print(f"   Latitud: {punto.latitud}")
        print(f"   Longitud: {punto.longitud}")
        print(f"   Potencia: {punto.potencia_kw} kW")
        print(f"   Estado: {getattr(punto, 'estado', 'no definido')}")
        
        # Verificar si tiene coordenadas válidas
        if punto.latitud and punto.longitud:
            print(f"   ✅ Coordenadas válidas: {punto.latitud}, {punto.longitud}")
        else:
            print(f"   ❌ Coordenadas faltantes")
            
    # Buscar específicamente Tesla en Palma Palmilla
    tesla_palma = puntos.filter(nombre__icontains='tesla', direccion__icontains='palma').first()
    if tesla_palma:
        print(f"\n🔍 TESLA ENCONTRADO EN PALMA:")
        print(f"   Nombre: {tesla_palma.nombre}")
        print(f"   Dirección: {tesla_palma.direccion}")
        print(f"   Coordenadas: {tesla_palma.latitud}, {tesla_palma.longitud}")
    else:
        print(f"\n❌ No se encontró Tesla en Palma")

if __name__ == "__main__":
    test_coordenadas()
