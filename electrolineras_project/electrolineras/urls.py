from django.urls import path
from .views import mapa_puntos_recarga, PuntoRecargaDetailView  # Corregido: importamos mapa_puntos_recarga
from . import api_views

urlpatterns = [
    path('mapa/', mapa_puntos_recarga, name='mapa_puntos_recarga'),
    path('punto_recarga/<int:pk>/', PuntoRecargaDetailView.as_view(), name='detalle_punto_recarga'),
    path('api/puntos/', api_views.PuntoRecargaListAPIView.as_view(), name='api_puntos'),
    path('api/reservas/', api_views.ReservaListCreateAPIView.as_view(), name='api_reservas'),
]
