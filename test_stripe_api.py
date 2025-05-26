#!/usr/bin/env python
"""
Script para probar la comunicación con la API de Stripe.
Este script verifica si la clave secreta de Stripe está configurada correctamente
y si es posible crear un PaymentIntent exitosamente.
"""

import os
import sys
import json
import stripe
import requests
from stripe.error import AuthenticationError, CardError, InvalidRequestError

# Añadir la ruta del proyecto para poder importar configuraciones de Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'electrolineras_project'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrolineras_project.settings')

# Importar configuraciones de Django (solo después de configurar el entorno)
try:
    from django.conf import settings
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
except (ImportError, ModuleNotFoundError):
    print("⚠️ No se pudo importar configuraciones de Django. Usando variables de entorno o valores por defecto.")
    # Usar variables de entorno o valores por defecto si no se puede cargar desde Django
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51RSBOfQFcvigGkXXhDJXIRboYegLXYXKqEY06QB40Mhah3qL87aG8CDpx9vFM4egiJ4M2Wt9LNCM4a018yQEdFHr00nYJvh5A7')
    stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_51RSBOfQFcvigGkXXijjkijmBd62X9byrfX8BA9NLUARc60ZwoaqvrNx9DkcwEZqahbjnIFhn2H5eDUSKYIzf7fMH00K6OcsDPl')

def test_stripe_connection():
    """Prueba la conexión básica con Stripe"""
    print("\n🧪 PRUEBA DE CONEXIÓN STRIPE")
    print("=" * 50)
    
    print(f"🔑 Usando clave secreta: {stripe_secret_key[:8]}...{stripe_secret_key[-4:]}")
    
    # Configurar Stripe con la clave secreta
    stripe.api_key = stripe_secret_key
    
    try:
        # Intentar obtener información de la cuenta
        account = stripe.Account.retrieve()
        print(f"✅ Conexión exitosa con Stripe")
        print(f"📊 Detalles de la cuenta:")
        print(f"   - ID: {account.id}")
        print(f"   - Email: {account.email}")
        print(f"   - País: {account.country}")
    except AuthenticationError as e:
        print(f"❌ Error de autenticación: {e}")
        print("→ Verifica que la clave secreta de Stripe sea válida")
        return False
    except Exception as e:
        print(f"❌ Error desconocido: {e}")
        return False
        return False

def test_create_payment_intent():
    """Prueba la creación de un PaymentIntent"""
    print("\n🧪 PRUEBA DE CREACIÓN DE PAYMENT INTENT")
    print("=" * 50)
    
    # Configurar Stripe con la clave secreta
    stripe.api_key = stripe_secret_key
    
    try:
        # Crear un PaymentIntent de prueba
        intent = stripe.PaymentIntent.create(
            amount=1000,  # 10.00 EUR en céntimos
            currency="eur",
            description="Prueba de integración",
            metadata={
                "test": "true",
                "source": "test_script"
            }
        )
        
        print(f"✅ PaymentIntent creado exitosamente")
        print(f"📊 Detalles del PaymentIntent:")
        print(f"   - ID: {intent.id}")
        print(f"   - Cliente: {intent.customer or 'No especificado'}")
        print(f"   - Estado: {intent.status}")
        print(f"   - Cliente Secret disponible: {'Sí' if intent.client_secret else 'No'}")
        print(f"   - Cantidad: {intent.amount/100} {intent.currency.upper()}")
        print(f"\n🔗 Link para probar en la dashboard de Stripe:")
        print(f"   https://dashboard.stripe.com/test/payments/{intent.id}")
    except CardError as e:
        print(f"❌ Error de tarjeta: {e}")
        return False
    except InvalidRequestError as e:
        print(f"❌ Error de solicitud inválida: {e}")
        return False
    except Exception as e:
        print(f"❌ Error desconocido: {e}")
        return False
        return False

def test_html_elements():
    """Comprueba si podemos cargar correctamente el formulario de elementos HTML"""
    print("\n🧪 PRUEBA DE ELEMENTOS HTML DE STRIPE")
    print("=" * 50)
    
    try:
        print("Intentando cargar el script de Stripe Elements...")
        response = requests.get('https://js.stripe.com/v3/')
        
        if response.status_code == 200:
            print(f"✅ Script de Stripe Elements accesible (Status: {response.status_code})")
            
            # Verificar headers relevantes
            content_type = response.headers.get('Content-Type', '')
            cors_header = response.headers.get('Access-Control-Allow-Origin', '')
            
            print(f"   - Content-Type: {content_type}")
            print(f"   - CORS Header: {cors_header}")
            
            if 'javascript' in content_type.lower() and cors_header == '*':
                print("   ✓ Headers correctos para cargar en navegador")
            else:
                print("   ⚠️ Headers podrían causar problemas de carga")
                
            return True
        else:
            print(f"❌ No se pudo acceder al script de Stripe Elements (Status: {response.status_code})")
            return False
    except ImportError:
        print("⚠️ Módulo 'requests' no instalado. Instalarlo con: pip install requests")
        return None
    except Exception as e:
        print(f"❌ Error al verificar acceso a Stripe Elements: {e}")
        return False

def test_api_crear_payment_intent(token, factura_id):
    """Prueba la API de creación de PaymentIntent con autenticación"""
    print("\n🧪 PRUEBA DE LA API DE CREACIÓN DE PAYMENT INTENT")
    print("=" * 50)
    
    # Definir la URL de la API
    url = "http://127.0.0.1:8000/payments/api/crear-payment-intent/"
    
    # Definir la carga útil
    payload = {
        "factura_id": factura_id  # Usar el ID de factura proporcionado
    }

    # Definir los headers, incluyendo el token de autorización
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"  # Incluir el token aquí
    }

    try:
        # Hacer la solicitud POST a la API
        response = requests.post(url, json=payload, headers=headers)

        # Imprimir la respuesta
        if response.status_code == 200:
            print("✅ Request a la API exitosa!")
            print("Response:", response.json())
            return True
        else:
            print(f"❌ Request a la API fallida con código de estado {response.status_code}")
            print("Response:", response.text)
            return False
    except Exception as e:
        print(f"❌ Error al probar la API de creación de PaymentIntent: {e}")
        return False

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🔍 DIAGNÓSTICO DE INTEGRACIÓN CON STRIPE")
    print("=" * 50)
    print(f"📅 Fecha de ejecución: {import_django_if_possible()}")
    
    # Ejecutar pruebas
    connection_ok = test_stripe_connection()
    
    if connection_ok:
        payment_intent_ok = test_create_payment_intent()
        elements_ok = test_html_elements()
        
        # Resumen
        print("\n📋 RESUMEN DE PRUEBAS")
        print("=" * 50)
        print(f"✓ Conexión a Stripe: {'ÉXITO ✅' if connection_ok else 'FALLO ❌'}")
        print(f"✓ Creación de PaymentIntent: {'ÉXITO ✅' if payment_intent_ok else 'FALLO ❌'}")
        print(f"✓ Acceso a Stripe Elements: {'ÉXITO ✅' if elements_ok else 'FALLO ❌' if elements_ok is not None else 'NO PROBADO ⚠️'}")
        
        # Diagnóstico y recomendaciones
        print("\n🩺 DIAGNÓSTICO Y RECOMENDACIONES")
        print("=" * 50)
        
        if not payment_intent_ok:
            print("→ Problema detectado con la creación de PaymentIntent en el backend")
            print("  Recomendación: Verificar la configuración de Stripe en settings.py")
        
        if not elements_ok and elements_ok is not None:
            print("→ Problema detectado con el acceso a Stripe Elements (frontend)")
            print("  Recomendación: Verificar la conectividad a js.stripe.com desde el navegador")
            
        if payment_intent_ok and (elements_ok or elements_ok is None):
            print("→ La API de Stripe funciona correctamente para crear PaymentIntents")
            print("  Si el formulario no aparece en el navegador, el problema probablemente está en el código frontend")
            print("  Recomendaciones:")
            print("   - Verificar la consola del navegador para errores JavaScript")
            print("   - Asegurarse de que el contenedor #card-element existe cuando se intenta montar el formulario")
            print("   - Revisar si hay restricciones CORS o CSP en el navegador")
    else:
        print("\n❌ La conexión con Stripe falló. No se pueden realizar pruebas adicionales.")
        print("→ Verifica la clave API de Stripe y tu conexión a internet.")

    # Probar la API de creación de PaymentIntent con un token de ejemplo y un ID de factura
    test_api_crear_payment_intent("abc123def456ghi789jkl", "38")

def import_django_if_possible():
    """Intenta importar Django para obtener la fecha actual"""
    try:
        import django
        django.setup()
        from django.utils import timezone
        return timezone.now()
    except Exception:
        from datetime import datetime
        return datetime.now()

if __name__ == "__main__":
    main()
