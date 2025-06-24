#!/usr/bin/env python
import os
import sys
import django
import asyncio

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrolineras_project.settings')
django.setup()

from chatbot.consumers import obtener_electrolineras_reales

async def test_chatbot_coordenadas():
    print("=== PRUEBA DE ACCESO A COORDENADAS EN EL CHATBOT ===")
    
    # Obtener electrolineras usando la función del chatbot
    electrolineras = await obtener_electrolineras_reales()
    
    print(f"\nElectrolineras obtenidas por el chatbot: {len(electrolineras)}")
    
    for electrolinera in electrolineras:
        print(f"\n📍 {electrolinera['nombre']}")
        print(f"   Dirección: {electrolinera['direccion']}")
        print(f"   Latitud: {electrolinera.get('latitud', 'N/A')}")
        print(f"   Longitud: {electrolinera.get('longitud', 'N/A')}")
        print(f"   Potencia: {electrolinera['potencia_kw']} kW")
        print(f"   Estado: {electrolinera['estado']}")
        print(f"   Conector: {electrolinera['conector']}")
        
        # Verificar las coordenadas
        if electrolinera.get('latitud') and electrolinera.get('longitud'):
            print(f"   ✅ Coordenadas disponibles para el chatbot")
        else:
            print(f"   ❌ Coordenadas no disponibles")
    
    print(f"\n=== SIMULACIÓN DE CONTEXTO PARA OLLAMA ===")
    
    # Simular el contexto que se enviaría a Ollama para una pregunta sobre Palma
    contexto_datos = "\nElectrolineras disponibles:\n"
    for electrolinera in electrolineras:
        contexto_datos += f"- {electrolinera['nombre']}: {electrolinera['direccion']}"
        if electrolinera.get('latitud') and electrolinera.get('longitud'):
            contexto_datos += f" (Coordenadas: {electrolinera['latitud']}, {electrolinera['longitud']})"
        contexto_datos += f", {electrolinera['potencia_kw']}kW, conector {electrolinera['conector']}, estado: {electrolinera['estado']}"
        if electrolinera.get('energia_total', 0) > 0:
            contexto_datos += f", energía total suministrada: {electrolinera['energia_total']} kWh"
        contexto_datos += "\n"
    
    print("Contexto que se enviaría a Ollama:")
    print(contexto_datos)

if __name__ == "__main__":
    asyncio.run(test_chatbot_coordenadas())
