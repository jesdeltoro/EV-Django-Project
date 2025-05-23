import requests
import json

url = "http://127.0.0.1:8000/electrolineras/api/iniciar-carga/"

data = {
    "reserva_id": 14  # Reemplaza con el ID real de la reserva
}

# Primero, obtener una sesión y login
session = requests.Session()

# Reemplaza con tus credenciales de login
login_data = {
    "username": "tuusuario",  # Reemplaza con tu nombre de usuario
    "password": "tupassword"  # Reemplaza con tu contraseña
}

# Obtener el token CSRF primero
response = session.get("http://127.0.0.1:8000/accounts/login/")
csrftoken = session.cookies.get("csrftoken")

headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrftoken
}

# Realizar el login primero
login_url = "http://127.0.0.1:8000/accounts/login/"
login_data = {
    "username": "tuusuario",  # Reemplaza con tu nombre de usuario
    "password": "tupassword"  # Reemplaza con tu contraseña
}

# Obtener csrf token para el login
login_page = session.get(login_url)
# Buscar el token csrf en la página
import re
csrf_token = re.search('name="csrfmiddlewaretoken" value="(.+?)"', login_page.text)
if csrf_token:
    login_data['csrfmiddlewaretoken'] = csrf_token.group(1)

# Realizar login
session.post(login_url, data=login_data, headers={"Referer": login_url})

# Una vez autenticado, realizar la petición a la API
response = session.post(url, data=json.dumps(data), headers=headers)

print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")
