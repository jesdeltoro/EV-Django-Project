from django.urls import path
from .views import mapa_puntos_recarga, PuntoRecargaDetailView  # Corregido: importamos mapa_puntos_recarga

urlpatterns = [
    path('mapa/', mapa_puntos_recarga, name='mapa_puntos_recarga'),
    path('punto_recarga/<int:pk>/', PuntoRecargaDetailView.as_view(), name='detalle_punto_recarga'),
]
