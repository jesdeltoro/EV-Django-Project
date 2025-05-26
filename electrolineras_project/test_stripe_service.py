"""
Script para probar la funcionalidad de StripeService.crear_payment_intent
"""
import os
import sys
import logging
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electrolineras_project.settings')
django.setup()

from payments.services import StripeService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_crear_payment_intent():
    """Prueba la función crear_payment_intent con diferentes valores"""
    
    # Probar con un monto normal
    print("Probando con 10.00 EUR")
    try:
        pi = StripeService.crear_payment_intent(Decimal('10.00'), metadata={'test': 'true'})
        print(f"✅ Éxito: {pi.id if pi else 'None'}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar con un monto pequeño (debería ajustarse automáticamente)
    print("\nProbando con 0.30 EUR (debería ajustarse a 0.50 EUR)")
    try:
        pi = StripeService.crear_payment_intent(Decimal('0.30'), metadata={'test': 'true'})
        print(f"✅ Éxito: {pi.id if pi else 'None'}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar con un string
    print("\nProbando con un string '5.00'")
    try:
        pi = StripeService.crear_payment_intent('5.00', metadata={'test': 'true'})
        print(f"✅ Éxito: {pi.id if pi else 'None'}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Iniciando prueba de StripeService.crear_payment_intent...\n")
    test_crear_payment_intent()
    print("\nPruebas completadas")
