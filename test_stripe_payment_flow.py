#!/usr/bin/env python
"""
Script para probar el flujo completo de procesamiento de pagos de una factura específica.
Este script simula todas las operaciones que realiza el frontend al procesar un pago.
"""

import os
import sys
import json
import stripe

# Añadir la ruta del proyecto para poder importar configuraciones de Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'electrolineras_project'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrolineras_project.settings')

try:
    print("Inicializando Django...")
    import django
    django.setup()
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from electrolineras_project.payments.models import Factura
    
    DJANGO_LOADED = True
    print("Django inicializado correctamente.")
except Exception as e:
    print(f"No se pudo inicializar Django: {e}")
    DJANGO_LOADED = False

# Configurar Stripe (con clave de configuración o por parámetro)
STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', None) if DJANGO_LOADED else None
if not STRIPE_SECRET_KEY:
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_51RSBOfQFcvigGkXXhDJXIRboYegLXYXKqEY06QB40Mhah3qL87aG8CDpx9vFM4egiJ4M2Wt9LNCM4a018yQEdFHr00nYJvh5A7')

stripe.api_key = STRIPE_SECRET_KEY

User = get_user_model() if DJANGO_LOADED else None

def get_facturas_pendientes():
    """Obtiene las facturas pendientes"""
    if not DJANGO_LOADED:
        print("Django no está inicializado. No se pueden obtener facturas.")
        return []
    
    try:
        facturas = Factura.objects.filter(estado='pendiente')
        return facturas
    except Exception as e:
        print(f"Error al obtener facturas pendientes: {e}")
        return []

def crear_payment_intent_para_factura(factura_id=None):
    """Crea un PaymentIntent para una factura específica o una prueba"""
    print(f"\n🧪 CREAR PAYMENT INTENT PARA FACTURA {factura_id or 'DE PRUEBA'}")
    print("=" * 50)
    
    try:
        # Si tenemos Django y una factura_id, usar datos reales
        if DJANGO_LOADED and factura_id:
            try:
                factura = Factura.objects.get(id=factura_id)
                print(f"Factura encontrada: {factura.numero_factura}")
                print(f"Total: {factura.total} EUR")
                print(f"Usuario: {factura.usuario}")
                
                # Crear PaymentIntent
                intent = stripe.PaymentIntent.create(
                    amount=int(factura.total * 100),  # Convertir a céntimos
                    currency="eur",
                    description=f"Pago factura {factura.numero_factura}",
                    metadata={
                        "factura_id": factura.pk,
                        "numero_factura": factura.numero_factura,
                        "usuario_id": factura.usuario.id if factura.usuario else "desconocido"
                    }
                )
            except Factura.DoesNotExist:
                print(f"❌ No se encontró la factura con ID {factura_id}")
                return None
            except Exception as e:
                print(f"❌ Error al obtener datos de la factura: {e}")
                return None
        else:
            # Crear un PaymentIntent de prueba
            intent = stripe.PaymentIntent.create(
                amount=1000,  # 10.00 EUR en céntimos
                currency="eur",
                description="Prueba de pago de factura",
                metadata={
                    "test": "true",
                    "source": "test_script"
                }
            )
        
        print(f"\n✅ PaymentIntent creado exitosamente")
        print(f"📊 Detalles del PaymentIntent:")
        print(f"   - ID: {intent.id}")
        print(f"   - Cliente Secret: {intent.client_secret[:15]}... (truncado)")
        print(f"   - Estado: {intent.status}")
        print(f"   - Cantidad: {intent.amount/100} {intent.currency.upper()}")
        
        # Mostrar instrucciones para el frontend
        print("\n📋 INSTRUCCIONES PARA FRONTEND:")
        print("Para confirmar este pago desde el frontend, usa:")
        print(f"const result = await stripe.confirmCardPayment('{intent.client_secret}', " + "{")
        print("  payment_method: { card: cardElement, billing_details: { name: 'Cliente' } }")
        print("});")
        
        return intent
    except stripe.error.StripeError as e:
        print(f"❌ Error de Stripe: {e}")
        return None
    except Exception as e:
        print(f"❌ Error desconocido: {e}")
        return None

def simular_confirmacion_pago(payment_intent_id):
    """Simula la confirmación de un pago desde el backend"""
    print(f"\n🧪 CONFIRMAR PAGO {payment_intent_id}")
    print("=" * 50)
    
    try:
        # Verificar el PaymentIntent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        print(f"PaymentIntent recuperado: {payment_intent.id}")
        print(f"Estado: {payment_intent.status}")
        
        # En un caso real, aquí verificaríamos que el estado es 'succeeded'
        # y actualizaríamos la factura en la base de datos
        if payment_intent.status == 'succeeded':
            print("✅ El pago fue exitoso")
            
            # Si Django está cargado, intentamos actualizar la factura
            if DJANGO_LOADED:
                try:
                    # Buscar factura por el payment_intent_id
                    factura = Factura.objects.get(stripe_payment_intent_id=payment_intent_id)
                    
                    # Actualizar estado
                    print(f"Actualizando factura {factura.numero_factura} a estado 'pagada'")
                    # No realizamos cambios reales para evitar modificar datos
                    
                    print("✅ Factura actualizada exitosamente (simulación)")
                except Factura.DoesNotExist:
                    print("❌ No se encontró la factura asociada al PaymentIntent")
                except Exception as e:
                    print(f"❌ Error al actualizar la factura: {e}")
        else:
            print(f"⚠️ El pago no está en estado 'succeeded', sino '{payment_intent.status}'")
        
        return payment_intent
    except stripe.error.StripeError as e:
        print(f"❌ Error de Stripe: {e}")
        return None
    except Exception as e:
        print(f"❌ Error desconocido: {e}")
        return None

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n🔍 PRUEBA DE PAGO DE FACTURA")
    print("=" * 50)
    print("1. Listar facturas pendientes")
    print("2. Crear PaymentIntent para una factura")
    print("3. Crear PaymentIntent de prueba")
    print("4. Verificar un PaymentIntent existente")
    print("5. Salir")
    return input("Seleccione una opción: ")

def main():
    """Función principal"""
    print("🔍 SIMULADOR DE PROCESO DE PAGO DE FACTURA")
    print("=" * 50)
    
    while True:
        opcion = mostrar_menu()
        
        if opcion == "1":
            if DJANGO_LOADED:
                facturas = get_facturas_pendientes()
                if facturas:
                    print("\n📋 FACTURAS PENDIENTES:")
                    for f in facturas:
                        print(f"ID: {f.id} | Número: {f.numero_factura} | Total: {f.total} EUR | Usuario: {f.usuario}")
                else:
                    print("No hay facturas pendientes.")
            else:
                print("Django no está inicializado. No se pueden listar facturas.")
                
        elif opcion == "2":
            if DJANGO_LOADED:
                factura_id = input("Ingrese el ID de la factura: ")
                try:
                    factura_id = int(factura_id)
                    intent = crear_payment_intent_para_factura(factura_id)
                    if intent and input("\n¿Desea simular confirmación del pago? (s/n): ").lower() == 's':
                        simular_confirmacion_pago(intent.id)
                except ValueError:
                    print("ID de factura inválido.")
            else:
                print("Django no está inicializado. No se puede acceder a facturas.")
                
        elif opcion == "3":
            intent = crear_payment_intent_para_factura()
            
        elif opcion == "4":
            payment_intent_id = input("Ingrese el ID del PaymentIntent a verificar: ")
            simular_confirmacion_pago(payment_intent_id)
            
        elif opcion == "5":
            print("\nSaliendo del simulador...")
            break
            
        else:
            print("Opción inválida.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
