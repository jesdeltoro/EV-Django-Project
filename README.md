# TECHNICAL DOCUMENTATION

## EvEMaps: Electric Vehicle Charging Station Management System

**Author:** Julio Schneider Estop
**Higher Vocational Training in Multiplatform Application Development**
**Portada Alta Secondary School**
**Final vocational training project — June 2025**

- Public website: https://evemaps.pythonanywhere.com
- APK: EvEMaps 1.0.4, version code 5, using OpenStreetMap
- Download: https://evemaps.pythonanywhere.com/download/evemaps-app/

---

## 1. INTRODUCTION AND OBJECTIVES

EvEMaps is a Django web application for managing electric-vehicle charging stations. Users can locate, reserve and use charging points through a responsive web interface. The project also exposes a REST API for mobile integrations.

Main objectives:

- Locate charging points on an interactive map.
- Reserve available charging points.
- Manage active charging sessions with real-time simulation.
- Provide administration tools for stations and users.
- Expose REST services for mobile applications.

The project models a professional system that could be extended for real-world deployment.

---

## 2. TECHNICAL ANALYSIS

### Technologies

Backend:

- Django 5.2 LTS
- Python 3.x
- SQLite for development
- Django REST Framework
- JWT authentication

Frontend:

- HTML5
- CSS3 and responsive design
- JavaScript
- TinyMCE rich-text editor

Libraries and tools:

- django-registration for user management
- Pillow for image processing
- PowerShell automation scripts
- Stripe PaymentIntents for payment integration
- Django Channels and WebSockets for real-time features

### Project structure

~~~text
EV-Django-Project/
├── .gitignore
├── README.md
├── requirements.txt
├── electrolineras_project/
│   ├── manage.py
│   ├── core/
│   ├── electrolineras/
│   ├── pages/
│   ├── messenger/
│   ├── payments/
│   ├── profiles/
│   ├── registration/
│   └── electrolineras_project/
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
├── Recursos/
└── test/
~~~

Generated files, virtual environments, databases, logs, uploaded media and editor files must remain excluded from version control.

### Applications

#### Pages

The Pages application manages blog posts and site content. It provides TinyMCE editing, staff-only permissions, CRUD operations, pagination, custom ordering and automatic timestamps.

Main URLs:

- /pages/
- /pages/create/
- /pages/<id>/<slug>/
- /pages/update/<id>/

#### Messenger

The Messenger application provides private communication between registered users. It includes private threads, AJAX message delivery, permission validation, automatic thread creation, activity timestamps and a responsive chat interface.

Main URLs:

- /messenger/
- /messenger/thread/<id>/
- /messenger/thread/<id>/add/
- /messenger/thread/start/<username>/

#### Registration and Profiles

This application manages registration, authentication and user profiles. It supports unique email addresses, avatars, biographies, website links, aliases, custom forms, password validation and automatic profile creation through Django signals.

Main URLs:

- /accounts/signup/
- /accounts/profile/
- /accounts/profile/email/
- /accounts/login/
- /accounts/password_change/

#### Payments

The Payments application manages invoices and charging-session payments through Stripe.

Features include:

- Automatic invoice creation after charging sessions.
- Dynamic energy rates.
- Stripe PaymentIntent creation and confirmation.
- Per-user invoice history.
- Administration and financial review.
- REST endpoints for rates, invoices, payments and statistics.
- Ownership and duplicate-payment validation.
- HTTPS, CSRF and environment-based secret configuration.

Main endpoints:

- /payments/api/tarifa/
- /payments/api/mis-facturas/
- /payments/api/crear-payment-intent/
- /payments/api/confirmar-pago/
- /payments/api/estadisticas/
- /payments/pagar/<invoice_id>/

Payment flow:

1. A user finishes a charging session.
2. The system creates an invoice from energy consumption and the active rate.
3. The user selects Pay from the invoice history.
4. The backend creates a Stripe PaymentIntent.
5. Stripe processes and confirms the payment.
6. The application validates the result and marks the invoice as paid.

Stripe secret keys must be supplied through environment variables and must never be committed.

#### Optional chatbot and Ollama integration

The repository contains an optional local chatbot integration. It is currently inactive in the default deployment.

- Ollama endpoint: http://localhost:11434/api/generate
- Configured model: llama3.2:3b
- Knowledge source: chatbot/knowledge_base.json and the ChatbotKnowledge model
- Setup helpers: instalar_ollama.ps1 and instalar_ollama_completo.ps1
- Maintenance guide: GUIA_ACTUALIZACION_CHATBOT.md

---

## 3. DATABASE DESIGN

The main domain models are:

- Connector: available connector types such as CCS and CHAdeMO.
- ChargingPoint: station location, power, connector and current status.
- Booking: user reservation with start and expiration dates.
- ChargingSession: active session, battery progress and energy consumption.
- Profile: user avatar, biography, website link and alias.
- Thread and Message: private user conversations.
- Invoice and Rate: charging costs, rates and Stripe payment references.

The main relationships are:

- User to Booking: one-to-many.
- Charging point to Booking: one-to-many.
- Booking to Charging Session: one-to-one.
- Connector to Charging Point: one-to-many.
- User to Profile: one-to-one.
- User to Thread: many-to-many.
- Thread to Message: many-to-many.

---

## 4. IMPLEMENTED FEATURES

### Authentication

- Registration and validation.
- Secure login and logout sessions.
- Profiles with avatars and biographies.
- JWT-authenticated mobile API.

### Charging-station management

- Interactive charging-point map.
- Available, in-use, reserved and out-of-service states.
- Detailed station information.
- Filtering and search by features.

### Booking and charging simulation

- Configurable bookings, with 30 minutes as the default.
- Automatic expiration of unused bookings.
- Real-time availability validation.
- Start and end of charging sessions.
- Battery-progress simulation.
- Energy calculation based on power and elapsed time.
- Prevention of multiple simultaneous sessions.

### Administration and REST API

- Charging-point management.
- User and profile administration.
- Active-session monitoring.
- Usage and energy statistics.
- Authentication, charging-point and booking endpoints.
- Automatic endpoint documentation.

### Management commands

~~~bash
python manage.py actualizar_baterias
python manage.py actualizar_baterias --intervalo 30
~~~

The command updates active sessions, simulates charging progress, detects full batteries, logs progress and supports configurable intervals.

### SEO and indexing

- Specific titles and descriptions.
- Canonical URLs, Open Graph and Schema.org structured data.
- Dynamic XML sitemap.
- robots.txt and noindex rules for private and transactional areas.
- Google Search Console verification.
- Permanent HTTPS redirection.

### Privacy and contact

- Cookie-consent manager with persistent preferences.
- Optional resources loaded only after consent.
- Public contact through julio@juliomalaga.online and Briar.

### Android application

The official APK is available at:

https://evemaps.pythonanywhere.com/download/evemaps-app/

| Data | Value |
|------|-------|
| Version | 1.0.4 |
| Version code | 5 |
| Map | OpenStreetMap |
| Size | 20,895,087 bytes |
| SHA-256 | 6A2FA344C6BBF658FCAA3BE9C52611E765943416BA66FB60BB3999D73C7C3674 |

The APK is signed with the same certificate as previous official versions, so Android can install it as an update.

---

## 5. SOFTWARE ARCHITECTURE

The project follows Django’s Model-Template-View pattern:

- Models define data structures, relationships and business logic.
- Views receive HTTP requests, interact with models and return responses.
- Templates define the presentation layer.

In MVC terminology, Django views fulfil approximately the controller role, while Django templates fulfil the view role.

Design principles:

- Separation of concerns.
- Modular and reusable code.
- Scalability.
- Maintainability.

Security controls:

- Input validation and sanitization.
- CSRF protection.
- Hashed passwords and secure sessions.
- Role-based authorization.
- Authenticated access to personal data and payments.
- Environment variables for external credentials.

---

## 6. INSTALLATION AND CONFIGURATION

### Requirements

~~~text
Django==5.2.17
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.0
django-registration==3.4
django-tinymce==4.1.0
Pillow==10.3.0
~~~

### Installation

Clone the repository:

~~~bash
git clone https://github.com/jesdeltoro/EV-Django-Project.git
cd EV-Django-Project
~~~

Create and activate a virtual environment:

~~~bash
python -m venv venv
venv\Scripts\activate
~~~

On Linux or macOS:

~~~bash
source venv/bin/activate
~~~

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Initialize the database:

~~~bash
cd electrolineras_project
python manage.py makemigrations
python manage.py migrate
~~~

Create an administrator:

~~~bash
python manage.py createsuperuser
~~~

Start the development server:

~~~bash
python manage.py runserver
~~~

### Automation scripts

- iniciar_app.ps1: automatic application startup.
- instalar_servicio.ps1: Windows service installation.
- crear_tarea_programada.ps1: scheduled-task creation.
- instalar_ollama.ps1: interactive Ollama setup.
- instalar_ollama_completo.ps1: automated Ollama setup.

The Ollama chatbot is optional and currently inactive.

---

## 7. TESTING AND VALIDATION

Test categories include:

- Unit tests for models and critical functions.
- REST API integration tests.
- Browser and interface tests.
- Load tests with concurrent users.

Validated use cases:

1. User registration and authentication.
2. Charging-point search and location.
3. Complete booking and charging process.
4. Administrative resource management.
5. API integration for external applications.

Example:

~~~python
import requests
import json

def test_register_user():
    pass

def test_login_user():
    pass
~~~

---

## 8. DEPLOYMENT AND PRODUCTION

Production settings:

~~~python
DEBUG = False
ALLOWED_HOSTS = ['evemaps.pythonanywhere.com']
SECURE_SSL_REDIRECT = True
~~~

The application is deployed on PythonAnywhere and publishes the map, blog, REST API, sitemap and Android download over HTTPS.

SMTP credentials are deployment secrets and must never be stored in
`settings.py`. Configure the following environment variables using values from
your email provider; `.env.example` documents the expected names without real
credentials:

~~~text
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=<smtp account>
EMAIL_HOST_PASSWORD=<new app password>
DEFAULT_FROM_EMAIL=<sender address>
~~~

After any credential exposure, revoke the old app password before configuring
a replacement in the private deployment environment.

Optimizations include efficient static-file serving, database indexes, query caching, CSS and JavaScript compression, semantic SEO metadata, a dynamic sitemap and cookie consent before optional resources are loaded.

Monitoring includes error logs, access logs, performance metrics and alerts for critical failures.

---

## 9. RESULTS AND FUTURE WORK

Achieved objectives:

- Complete charging-station management system.
- Responsive user interface.
- Functional REST API.
- Realistic charging simulation.
- Security validation and access controls.
- Technical project documentation.

Potential improvements:

- Integration with production map services.
- Native React Native or Flutter application.
- Expanded payment methods.
- Machine learning for charging optimization.
- IoT connectivity with physical charging hardware.

---

## 10. MAIN URLS

~~~text
/                                   Home page
/mapa/                              Charging-station map
/admin/                             Administration panel
/accounts/                          Authentication
/profiles/                          User profiles
/api/token/                         Authentication API
/electrolineras/                    Charging-point management
/pages/                             Blog and news
/messenger/                         Messaging system
/payments/                          Payment API and UI
/payments/api/tarifa/               Current energy rate
/payments/api/mis-facturas/         User invoice list
/payments/api/crear-payment-intent/ Create a Stripe PaymentIntent
/payments/api/confirmar-pago/       Confirm payment status
/payments/api/estadisticas/         Payment and invoice statistics
/payments/pagar/<invoice_id>/       Invoice payment page
~~~

---

## CERTIFICATION

This document provides the technical documentation for the Electric Vehicle Charging Station Management System, developed as a final project for the Higher Vocational Training programme in Multiplatform Application Development.

**Author:** Julio Schneider Estop
**Repository:** https://github.com/jesdeltoro/EV-Django-Project
**Date:** June 2025
**Main technology:** Django 5.2 LTS and Python

The project demonstrates skills in:

- Full-stack web development.
- Database design.
- Object-oriented programming.
- REST APIs and web services.
- Software-project management.
- Professional technical documentation.
