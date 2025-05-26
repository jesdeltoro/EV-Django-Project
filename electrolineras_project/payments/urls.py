from django.urls import path
from . import views
from .views import CrearPaymentIntentAPIView

app_name = 'payments'

urlpatterns = [
    # APIs para pagos
    path('api/tarifa/', views.TarifaAPIView.as_view(), name='tarifa-api'),
    path('api/mis-facturas/', views.FacturasUsuarioAPIView.as_view(), name='facturas-api'),
    path('api/crear-payment-intent/', CrearPaymentIntentAPIView.as_view(), name='crear_payment_intent'),
    path('api/confirmar-pago/', views.ConfirmarPagoAPIView.as_view(), name='confirmar-pago'),
    path('api/estadisticas/', views.estadisticas_usuario, name='estadisticas-api'),
    
    # Webhook de Stripe
    path('webhook/stripe/', views.stripe_webhook, name='stripe-webhook'),
    # Página de pago de factura
    path('pagar/<int:factura_id>/', views.PagarFacturaView.as_view(), name='pagar'),
    # Página de listado de facturas
    path('facturas/', views.FacturasListView.as_view(), name='facturas'),
]
