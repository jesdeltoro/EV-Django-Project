import requests
import json

# URL de la API para crear PaymentIntent
url_crear_payment_intent = "http://127.0.0.1:8000/payments/api/crear-payment-intent/"

# Token de autenticación
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ4Mjg4NDM5LCJpYXQiOjE3NDgyODQ4MzksImp0aSI6IjIyZmJhYjg3NDEzYTQ1ZGJhYjBlNWRiM2VmNDk3NWIwIiwidXNlcl9pZCI6MTJ9.DGiiDmEjxmrng0Gs8g6cUWyC0Zcx7Hlh531FJgW0VgM"

# Define el payload
payload_crear_payment_intent = {
    "factura_id": 49  # Reemplaza con el factura_id real que deseas probar
}

# Define los headers
headers_crear_payment_intent = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# Debug: Verificar headers y payload
print("Headers para crear PaymentIntent:", headers_crear_payment_intent)
print("Payload para crear PaymentIntent:", payload_crear_payment_intent)

# Realizar la petición POST
try:
    response_crear_payment_intent = requests.post(
        url_crear_payment_intent,
        json=payload_crear_payment_intent,
        headers=headers_crear_payment_intent
    )

    # Imprimir la respuesta
    if response_crear_payment_intent.status_code == 200:
        print("✅ Request successful!")
        print("Response:", json.dumps(response_crear_payment_intent.json(), indent=4))
    else:
        print(f"❌ Request failed with status code {response_crear_payment_intent.status_code}")
        print("Response:", response_crear_payment_intent.text)

except requests.exceptions.RequestException as e:
    print(f"❌ Error en la solicitud: {e}")
