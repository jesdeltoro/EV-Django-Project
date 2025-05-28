# DOCUMENTACIÓN TÉCNICA
## SISTEMA DE GESTIÓN DE ELECTROLINERAS
### Trabajo Fin de Grado - FP DAM
### Autor: Julio Schneider Estop
### Fecha: Mayo 2025

---

## 1. INTRODUCCIÓN Y OBJETIVOS

### 1.1 Descripción del Proyecto
El proyecto "Sistema de Gestión de Electrolineras" es una aplicación web desarrollada en Django que permite gestionar puntos de recarga para vehículos eléctricos. La aplicación facilita a los usuarios localizar, reservar y utilizar puntos de carga mediante una interfaz web intuitiva y un API REST para integraciones móviles.

### 1.2 Objetivos Principales
- **Localización de puntos de carga**: Mapa interactivo con ubicaciones de electrolineras
- **Sistema de reservas**: Permitir a usuarios reservar puntos de carga
- **Gestión de sesiones**: Control de cargas activas con simulación en tiempo real
- **Administración**: Panel de control para gestionar puntos y usuarios
- **API REST**: Servicios web para integración con aplicaciones móviles

### 1.3 Justificación
Con el crecimiento del parque de vehículos eléctricos, existe una necesidad real de sistemas que faciliten la gestión y uso de infraestructuras de carga. Este proyecto simula un sistema profesional que podría implementarse en el mundo real.

---

## 2. ANÁLISIS TÉCNICO

### 2.1 Tecnologías Utilizadas

#### Backend
- **Django 5.2.1**: Framework web principal
- **Python 3.x**: Lenguaje de programación
- **SQLite**: Base de datos (desarrollo)
- **Django REST Framework**: API REST
- **JWT**: Autenticación de tokens

#### Frontend
- **HTML5**: Estructura de páginas
- **CSS3**: Estilos y diseño responsivo
- **JavaScript**: Interactividad del cliente
- **TinyMCE**: Editor de contenido enriquecido

#### Herramientas y Librerías
- **django-registration**: Gestión de usuarios
- **Pillow**: Procesamiento de imágenes
- **PowerShell**: Scripts de automatización

### 2.2 Arquitectura del Sistema

```
EV-Django-Project/
├── crear_tarea_programada.ps1         # Script PowerShell para programar tareas automáticas
├── iniciar_app.ps1                    # Script PowerShell para iniciar la app automáticamente
├── instalar_servicio.ps1              # Script PowerShell para instalar como servicio en Windows
├── EV-Django-Project.code-workspace   # Configuración del espacio de trabajo para VS Code
├── README.md                          # Documentación principal del proyecto
├── requirements.txt                   # Lista de dependencias del proyecto
├── test_api.py                        # Pruebas automatizadas para la API
├── electrolineras_project/            # Carpeta principal del proyecto Django
│   ├── manage.py                      # Comando principal para administrar Django
│   ├── db.sqlite3                     # Base de datos SQLite utilizada en desarrollo
│   ├── debug_serializer.py            # Utilidad para depuración y serialización de datos
│   ├── core/                          # Aplicación principal (core) del proyecto
│   ├── electrolineras/                # App para la gestión de electrolineras
│   ├── pages/                         # App para la gestión de páginas estáticas o dinámicas
│   ├── messenger/                     # App para funcionalidades de mensajería
│   ├── payments/                      # App para gestión de pagos y transacciones
│   ├── profiles/                      # App para gestión de perfiles de usuario
│   ├── registration/                  # App para gestión de registro y autenticación
│   ├── sent_emails/                   # Carpeta para almacenamiento de emails enviados (desarrollo)
│   └── electrolineras_project/        # Configuración principal de la instancia Django
│       ├── __init__.py                # Inicialización del paquete de configuración
│       ├── settings.py                # Configuración global del proyecto Django
│       ├── urls.py                    # Definición de rutas/URLs del proyecto
│       └── wsgi.py                    # Punto de entrada para servidores WSGI
└── Recursos/                          # Carpeta para recursos adicionales (imágenes, documentación, etc.)
```


### 2.3 Aplicaciones del Sistema

#### 📝 Aplicación Pages (Gestión de Blog)
**Propósito**: Sistema de gestión de contenido para noticias y blog del sitio web.

**Funcionalidades principales:**
- **Editor TinyMCE integrado** para contenido enriquecido con formato HTML
- **Sistema de permisos restringido** a usuarios staff para crear/editar contenido
- **CRUD completo** (Crear, Leer, Actualizar, Eliminar) para páginas de blog
- **Visualización paginada** en la página principal con últimas noticias
- **Orden personalizable** de entradas mediante campo de orden
- **Timestamps automáticos** de creación y última edición
- **Integración visual** con tema violeta del sitio web

**Modelo Page:**
```python
class Page(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()  # Campo TinyMCE para contenido enriquecido
    order = models.SmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
```

**URLs principales:**
- `/pages/` - Lista de todas las páginas del blog
- `/pages/create/` - Crear nueva página (solo staff)
- `/pages/<id>/<slug>/` - Ver página específica
- `/pages/update/<id>/` - Editar página (solo staff)

#### 💬 Aplicación Messenger (Sistema de Mensajería)
**Propósito**: Sistema de mensajería privada entre usuarios registrados del sistema.

**Funcionalidades principales:**
- **Hilos de conversación privados** entre pares de usuarios
- **Mensajes en tiempo real** mediante AJAX sin recargar la página
- **Interfaz de chat moderna** con burbujas diferenciadas por usuario
- **Validación de permisos** que previene acceso no autorizado a conversaciones
- **ThreadManager personalizado** para encontrar o crear hilos automáticamente
- **Actualización automática** de timestamps de última actividad
- **Navegación fluida** entre diferentes conversaciones activas
- **Scroll automático** a mensajes más recientes

**Modelos principales:**
```python
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

class Thread(models.Model):
    users = models.ManyToManyField(User, related_name='threads')
    messages = models.ManyToManyField(Message)
    updated = models.DateTimeField(auto_now=True)
    objects = ThreadManager()
```

**Características técnicas avanzadas:**
- **Signal handlers** para validar que solo usuarios del hilo pueden enviar mensajes
- **AJAX endpoints** para envío asíncrono de mensajes
- **JavaScript dinámico** para actualización de interfaz en tiempo real
- **Gestión de estados** para el botón de envío

**URLs principales:**
- `/messenger/` - Lista de conversaciones del usuario
- `/messenger/thread/<id>/` - Conversación específica
- `/messenger/thread/<id>/add/` - Enviar mensaje (AJAX)
- `/messenger/thread/start/<username>/` - Iniciar nueva conversación

#### 🔐 Aplicación Registration (Registro y Perfiles)
**Propósito**: Sistema completo de autenticación, registro de usuarios y gestión de perfiles.

**Funcionalidades principales:**
- **Registro personalizado** con email obligatorio y validación de unicidad
- **Gestión completa de perfiles** con avatar, biografía, enlace web y alias
- **Formularios Django personalizados** con validación avanzada y styling
- **Actualización separada de email** con verificación anti-duplicados
- **Creación automática de perfil** mediante Django signals
- **Validación robusta** de contraseñas y datos de entrada
- **Integración visual** con el tema del sitio web
- **Gestión de archivos** para avatares con reemplazo automático

**Modelo Profile:**
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True)
    alias = models.CharField(max_length=100, null=True, blank=True, unique=True)
```

**Formularios especializados:**
- **UserCreationFormWithEmail**: Extiende el formulario base añadiendo email obligatorio
- **ProfileForm**: Gestión completa del perfil del usuario
- **EmailForm**: Actualización específica y validada del email

**Características técnicas:**
- **Django signals** para creación automática de perfil al registrar usuario
- **Validación personalizada** en formularios para prevenir duplicados
- **Upload personalizado** de avatares con eliminación del anterior
- **Decoradores de seguridad** para proteger vistas sensibles

**URLs principales:**
- `/accounts/signup/` - Registro de nuevos usuarios
- `/accounts/profile/` - Editar perfil completo
- `/accounts/profile/email/` - Actualizar solo email
- `/accounts/login/` - Inicio de sesión
- `/accounts/password_change/` - Cambio de contraseña

---

#### 💳 Aplicación Payments (Sistema de Pagos)

**Propósito:**  
La aplicación `payments` gestiona la facturación y los pagos de sesiones de carga para usuarios registrados, integrando procesamiento real con Stripe para simular un entorno profesional y seguro de transacciones. Permite que cada usuario visualice sus facturas, consulte tarifas, realice pagos y acceda a estadísticas de consumo y gasto.

**Funcionalidades principales:**
- **Generación automática de facturas** al finalizar cada sesión de carga.
- **Gestión de tarifas** dinámicas consultables vía API.
- **Integración con Stripe** para pagos seguros (PaymentIntent y confirmación de pago).
- **Historial de facturas** personalizadas para cada usuario.
- **Panel de administración** para revisión de pagos y control financiero.
- **API RESTful** para consultas, pagos y estadísticas.
- **Notificaciones automáticas** tras pago exitoso (opcional: email, logs).
- **Estadísticas detalladas** de pagos y consumo energético.

**Modelos principales:**
```python
class Tarifa(models.Model):
    nombre = models.CharField(max_length=50)
    precio_kwh = models.DecimalField(max_digits=5, decimal_places=2)
    activa = models.BooleanField(default=True)

class Factura(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sesion_carga = models.OneToOneField('SesionCarga', on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    energia_consumida = models.FloatField()
    total = models.DecimalField(max_digits=7, decimal_places=2)
    pagada = models.BooleanField(default=False)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
```
> **Nota:** El modelo `Tarifa` permite modificar el precio por kWh dinámicamente, y la relación uno a uno entre `Factura` y `SesionCarga` garantiza la trazabilidad de cada pago.

**Servicios y lógica de negocio (services.py):**
- **Cálculo automático del importe** al emitir una factura:  
  ```python
  total = energia_consumida * tarifa_activa.precio_kwh
  ```
- **Creación y gestión de PaymentIntent** con Stripe para cada factura pendiente.
- **Verificación y actualización del estado de pago** tras confirmación de Stripe.
- **Sincronización automática** de facturas y pagos mediante señales de Django.

**Endpoints y URLs principales:**
- `/payments/api/tarifa/` – Consulta la tarifa de energía actual.
- `/payments/api/mis-facturas/` – Devuelve el listado de facturas del usuario autenticado.
- `/payments/api/crear-payment-intent/` – Crea un PaymentIntent de Stripe para una factura pendiente.
- `/payments/api/confirmar-pago/` – Confirma el pago de una factura tras la devolución de Stripe.
- `/payments/api/estadisticas/` – Proporciona estadísticas de consumo y pagos realizados.
- `/payments/pagar/<factura_id>/` – Página web para el pago de una factura concreta.

**Flujo típico de pago:**
1. El usuario finaliza una sesión de carga.
2. Se genera automáticamente la factura con la energía consumida y el importe.
3. El usuario accede a su historial de facturas y selecciona “Pagar”.
4. Se crea un PaymentIntent en Stripe y se muestra el formulario de pago seguro.
5. Stripe procesa el pago y devuelve la confirmación.
6. El backend valida el pago y actualiza el estado de la factura a “pagada”.

**Integración con Stripe:**
- Uso de **PaymentIntent** para pagos seguros, compatible con tarjetas y métodos alternativos.
- **Webhook opcional** para gestionar pagos asíncronos y verificar el estado real en Stripe.
- Almacenamiento del `stripe_payment_intent` en la factura para trazabilidad y auditoría.
- Protección contra pagos duplicados y validación estricta de los datos recibidos.

**Seguridad y validaciones:**
- Acceso a facturas y endpoints restringido a usuarios autenticados.
- Comprobación de propiedad: solo el usuario dueño puede consultar o pagar sus facturas.
- Validación del importe y la sesión de carga antes de crear el intent de pago.
- Uso de HTTPS y CSRF para formularios y endpoints sensibles.
- Manejo seguro de claves API de Stripe mediante variables de entorno y configuración en `settings.py`.

**Ejemplo de uso (pseudocódigo):**
```python
# Crear factura al terminar sesión
factura = Factura.objects.create(
    usuario=request.user,
    sesion_carga=sesion,
    energia_consumida=sesion.energia_consumida,
    total=sesion.energia_consumida * tarifa.precio_kwh
)

# Crear PaymentIntent (en services.py)
payment_intent = stripe.PaymentIntent.create(
    amount=int(factura.total * 100),  # en céntimos
    currency='eur',
    metadata={'factura_id': factura.id}
)
factura.stripe_payment_intent = payment_intent['id']
factura.save()
```

**Consideraciones de diseño:**
- El sistema está preparado para soportar múltiples métodos de pago en el futuro.
- La arquitectura desacopla la lógica de facturación y el procesamiento externo de pagos.
- El usuario nunca expone datos sensibles; todo el flujo de pago ocurre en Stripe.
- Las estadísticas permiten al usuario y al administrador monitorizar el gasto y consumo eléctrico.

**Mejoras futuras posibles:**
- Soporte para **pagos recurrentes** o domiciliaciones.
- Integración de **facturación electrónica** (PDF automático, envío por email).
- Soporte para **descuentos/promociones** y cupones.
- Exportación de informes para contabilidad.

---

## 3. DISEÑO DE LA BASE DE DATOS

### 3.1 Modelos Principales

#### Conector
```python
class Conector(models.Model):
    codigo = models.IntegerField(primary_key=True)
    denominacion = models.CharField(max_length=100)
    potencia_kw = models.FloatField(null=True, blank=True)
```
**Función**: Define los tipos de conectores disponibles (CCS, CHAdeMO, etc.)

#### PuntoRecarga
```python
class PuntoRecarga(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=250)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    potencia_kw = models.FloatField(null=True, blank=True)
    tipo_conector = models.ForeignKey(Conector, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    energia_suministrada_total = models.FloatField(default=0)
    energia_actual_sesion = models.FloatField(default=0)
```
**Función**: Representa cada punto de carga con su ubicación, características técnicas y estado actual.

#### Reserva
```python
class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    punto = models.ForeignKey("PuntoRecarga", on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField()
```
**Función**: Gestiona las reservas de puntos de carga con expiración automática.

#### SesionCarga
```python
class SesionCarga(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    punto_recarga = models.ForeignKey(PuntoRecarga, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    porcentaje_bateria_inicial = models.IntegerField(default=20)
    porcentaje_bateria_actual = models.IntegerField(default=20)
    energia_consumida = models.FloatField(default=0)
```
**Función**: Controla sesiones de carga activas con simulación de progreso de batería.

### 3.2 Relaciones Entre Modelos
- **Usuario ↔ Reserva**: Relación uno a muchos
- **PuntoRecarga ↔ Reserva**: Relación uno a muchos
- **Reserva ↔ SesionCarga**: Relación uno a uno
- **Conector ↔ PuntoRecarga**: Relación uno a muchos
- **Usuario ↔ Profile**: Relación uno a uno (registration)
- **Usuario ↔ Thread**: Relación muchos a muchos (messenger)
- **Thread ↔ Message**: Relación muchos a muchos (messenger)

---

## 4. FUNCIONALIDADES IMPLEMENTADAS

### 4.1 Sistema de Autenticación
- **Registro de usuarios** con validación de datos
- **Login/Logout** con sesiones seguras
- **Gestión de perfiles** con avatares y biografías
- **API con autenticación JWT** para aplicaciones móviles

### 4.2 Gestión de Electrolineras
- **Mapa interactivo** mostrando ubicaciones de puntos de carga
- **Estados en tiempo real**: Disponible, En Uso, Reservado, Fuera de Servicio
- **Información detallada** de cada punto (potencia, tipo de conector, ubicación)
- **Filtrado y búsqueda** de puntos por características

### 4.3 Sistema de Reservas
- **Reserva de puntos** con duración configurable (30 minutos por defecto)
- **Expiración automática** de reservas no utilizadas
- **Validación de disponibilidad** en tiempo real
- **Historial de reservas** por usuario

### 4.4 Simulador de Carga
- **Inicio/fin de sesiones** de carga
- **Simulación de progreso** de batería en tiempo real
- **Cálculo de energía consumida** basado en potencia y tiempo
- **Actualización automática** de estados de puntos
- **Prevención de sesiones múltiples** por usuario

### 4.5 Panel de Administración
- **Gestión completa** de puntos de carga
- **Administración de usuarios** y perfiles
- **Monitorización de sesiones** activas
- **Estadísticas de uso** y energía suministrada

### 4.6 API REST
- **Endpoints de autenticación** (login, registro, refresh tokens)
- **Servicios de consulta** de puntos de carga
- **Gestión de reservas** vía API
- **Documentación automática** de endpoints

### 4.7 Sistema de Blog y Contenido (Pages)
- **Gestión de noticias** relacionadas con movilidad eléctrica
- **Editor enriquecido** con TinyMCE para contenido formateado
- **Publicación restringida** solo a usuarios staff autorizados
- **Visualización paginada** en página principal con últimas entradas

### 4.8 Sistema de Mensajería (Messenger)
- **Comunicación privada** entre usuarios registrados
- **Interfaz de chat** moderna y responsiva
- **Mensajería en tiempo real** sin recargar página
- **Gestión segura** de permisos por conversación

### 4.9 Gestión Avanzada de Usuarios (Registration)
- **Registro con email único** y validación robusta
- **Perfiles completos** con avatar, biografía y enlaces
- **Actualización granular** de datos de usuario
- **Integración automática** entre usuario y perfil

### 4.10 Sistema de Comandos de Management
- **Actualización automática de baterías** mediante comando `actualizar_baterias`
- **Simulación en tiempo real** del progreso de carga de vehículos
- **Monitorización continua** de sesiones activas con logs detallados
- **Configuración flexible** de intervalos de actualización
- **Notificaciones automáticas** cuando las baterías alcanzan el 100%
- **Gestión de procesos** en segundo plano para automatización del sistema
- **Scripts de mantenimiento** para corrección de estados y verificaciones

**Comando principal:**
```bash
# Ejecutar simulador de carga con intervalo por defecto (60 segundos)
python manage.py actualizar_baterias

# Ejecutar con intervalo personalizado
python manage.py actualizar_baterias --intervalo 30
```

**Funcionalidades del comando:**
- Actualiza automáticamente el porcentaje de batería de todas las sesiones activas
- Simula el proceso real de carga de vehículos eléctricos
- Proporciona feedback en tiempo real sobre el progreso de cada sesión
- Detecta automáticamente cuando las baterías alcanzan el 100%
- Permite configurar la frecuencia de actualización según necesidades

### 4.11 Payments

- **Procesamiento de pagos** para sesiones de carga
- **Integración con pasarelas de pago** (por ejemplo, Stripe.)
- **Generación de facturas** y recibos automáticos
- **Historial de transacciones** accesible para el usuario
- **Validación y seguridad** en el manejo de datos financieros
- **Notificaciones automáticas** de pago exitoso o fallido

---

## 5. ARQUITECTURA DE SOFTWARE

### 5.1 Patrón Modelo‑Template‑Vista (MTV)

* **Modelos**: Definen la estructura de datos, las relaciones entre tablas y la lógica de negocio.
* **Vistas (`views.py`)**: Reciben las peticiones HTTP, interactúan con los modelos y devuelven la respuesta adecuada (generalmente renderizando un template). En términos del patrón MVC, estas vistas cumplen el rol de *Controlador*.
* **Templates**: Archivos HTML (u otros formatos) que definen la presentación de los datos para el usuario final.

> **Nota:** Aunque el código de Django se organiza en `models`, `views` y `templates`, la documentación oficial se refiere al patrón como MTV, donde la capa de «Vista» se corresponde con el *Controller* de MVC y la capa de «Template» con la *View* de MVC.

#### Recursos

* **FAQ – “MVC” vs “MTV”** – [https://docs.djangoproject.com/en/5.2/faq/general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-dont-use-the-standard-names](https://docs.djangoproject.com/en/5.2/faq/general/#django-appears-to-be-a-mvc-framework-but-you-call-the-controller-the-view-and-the-view-the-template-how-come-you-dont-use-the-standard-names)
* **Glosario – término “MTV”** – [https://docs.djangoproject.com/en/5.2/glossary/#term-mtv](https://docs.djangoproject.com/en/5.2/glossary/#term-mtv)


### 5.2 Principios de Diseño Aplicados
- **Separación de responsabilidades**: Cada app tiene una función específica
- **Reutilización de código**: Componentes modulares y mixins
- **Escalabilidad**: Arquitectura preparada para crecimiento
- **Mantenibilidad**: Código documentado y bien estructurado

### 5.3 Seguridad Implementada
- **Validación de entrada**: Sanitización de datos de usuario
- **Protección CSRF**: Tokens de seguridad en formularios
- **Autenticación robusta**: Passwords hasheados y sesiones seguras
- **Autorización por roles**: Restricciones basadas en permisos

---

## 6. INSTALACIÓN Y CONFIGURACIÓN

### 6.1 Requisitos del Sistema
```
Django==5.2.1
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.0
django-registration==3.4
django-tinymce==4.1.0
Pillow==10.3.0
```

### 6.2 Proceso de Instalación

#### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/jesdeltoro/EV-Django-Project.git
cd EV-Django-Project
```

#### Paso 2: Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

#### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

#### Paso 4: Configurar base de datos
```bash
cd electrolineras_project
python manage.py makemigrations
python manage.py migrate
```

#### Paso 5: Crear superusuario
```bash
python manage.py createsuperuser
```

#### Paso 6: Iniciar servidor
```bash
python manage.py runserver
```

### 6.3 Scripts de Automatización
- **iniciar_app.ps1**: Script PowerShell para inicio automático
- **instalar_servicio.ps1**: Instalación como servicio Windows
- **crear_tarea_programada.ps1**: Programación de tareas automáticas

---

## 7. TESTING Y VALIDACIÓN

### 7.1 Pruebas Realizadas
- **Pruebas unitarias** de modelos y funciones críticas
- **Pruebas de integración** de API REST
- **Pruebas de interfaz** en diferentes navegadores
- **Pruebas de carga** con múltiples usuarios simultáneos

### 7.2 Casos de Uso Validados
1. **Registro y autenticación** de usuarios
2. **Búsqueda y localización** de puntos de carga
3. **Proceso completo** de reserva y carga
4. **Gestión administrativa** de recursos
5. **Integración API** para aplicaciones externas

### 7.3 Archivo de Pruebas API
```python
# test_api.py - Pruebas automatizadas de endpoints
import requests
import json

def test_register_user():
    """Prueba registro de nuevo usuario"""
    # Implementación de pruebas...

def test_login_user():
    """Prueba autenticación de usuario"""
    # Implementación de pruebas...
```

---

## 8. DESPLIEGUE Y PRODUCCIÓN

### 8.1 Configuración de Producción
```python
# settings.py - Configuraciones para producción
DEBUG = False
ALLOWED_HOSTS = ['mi-dominio.com', 'www.mi-dominio.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

### 8.2 Optimizaciones Implementadas
- **Archivos estáticos** servidos eficientemente
- **Base de datos** optimizada con índices
- **Cache** de consultas frecuentes
- **Compresión** de recursos CSS/JavaScript

### 8.3 Monitorización
- **Logs detallados** de errores y accesos
- **Métricas de rendimiento** de la aplicación
- **Alertas automáticas** para fallos críticos

---

## 9. RESULTADOS Y CONCLUSIONES

### 9.1 Objetivos Alcanzados
✅ **Sistema completo** de gestión de electrolineras
✅ **Interfaz intuitiva** y responsiva
✅ **API REST funcional** para integraciones
✅ **Simulación realista** de procesos de carga
✅ **Seguridad robusta** y validación de datos
✅ **Documentación completa** del proyecto

### 9.2 Aprendizajes Técnicos
- **Desarrollo web completo** con Django
- **Diseño de APIs RESTful** profesionales
- **Gestión de estados** en aplicaciones complejas
- **Simulación de procesos** de tiempo real
- **Integración de múltiples tecnologías**

### 9.3 Posibles Mejoras Futuras
- **Integración con mapas reales** (Google Maps, OpenStreetMap)
- **Aplicación móvil nativa** con React Native/Flutter
- **Sistema de pagos** integrado
- **Machine Learning** para optimización de carga
- **IoT** para conexión con hardware real

---

## 10. ANEXOS

### 10.1 Estructura Completa del Proyecto
```
EV-Django-Project/
├── crear_tarea_programada.ps1
├── iniciar_app.ps1
├── instalar_servicio.ps1
├── EV-Django-Project.code-workspace
├── README.md
├── requirements.txt
├── test_api.py
├── electrolineras_project/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── debug_serializer.py
│   ├── core/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── electrolineras/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── pages/
│   ├── messenger/
│   ├── payments/
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── views.py
│   │   └── templates/
│   ├── profiles/
│   ├── registration/
│   ├── sent_emails/
│   └── electrolineras_project/
│       ├── __init__.py
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
└── Recursos/
```

### 10.2 Configuraciones Clave
```python
# settings.py - Configuraciones principales
INSTALLED_APPS = [
    'registration',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'electrolineras',
    'profiles',
    'core',
    'messenger',
    'payments',
    'rest_framework',
    'pages.apps.PagesConfig',
    'tinymce',
]

LANGUAGE_CODE = 'es'
TIME_ZONE = 'Europe/Madrid'
```

### 10.3 URLs Principales
```python
# URLs del sistema
/                    # Página principal
/mapa/               # Mapa de electrolineras
/admin/              # Panel de administración
/accounts/           # Autenticación
/profiles/           # Perfiles de usuario
/api/token/          # API de autenticación
/electrolineras/     # Gestión de puntos de recarga
/pages/              # Blog y noticias
/messenger/          # Sistema de mensajería
/payments/           # Sistema de pagos (API y UI)
/payments/api/tarifa/               # Tarifa de energía actual
/payments/api/mis-facturas/         # Listado de facturas del usuario
/payments/api/crear-payment-intent/ # Crear PaymentIntent en Stripe
/payments/api/confirmar-pago/       # Confirmar estado de pago
/payments/api/estadisticas/         # Estadísticas de pagos y facturas
/payments/pagar/<factura_id>/       # Página de pago de factura
```

---

## CERTIFICACIÓN

Este documento constituye la documentación técnica completa del proyecto "Sistema de Gestión de Electrolineras", desarrollado como Trabajo Fin de Grado para el ciclo formativo de Desarrollo de Aplicaciones Multiplataforma (DAM).

**Autor**: Julio Schneider Estop  
**Repositorio**: https://github.com/jesdeltoro/EV-Django-Project  
**Fecha**: Mayo 2024  
**Tecnología Principal**: Django 5.2.1 + Python  

El proyecto demuestra competencias en:
- Desarrollo web full-stack
- Diseño de bases de datos
- Programación orientada a objetos
- APIs REST y servicios web
- Gestión de proyectos de software
- Documentación técnica profesional
