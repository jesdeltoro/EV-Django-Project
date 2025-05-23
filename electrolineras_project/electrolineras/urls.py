from django.urls import path
from .views import mapa_puntos_recarga, PuntoRecargaDetailView, iniciar_carga_view
from . import api_views

urlpatterns = [
    path('mapa/', mapa_puntos_recarga, name='mapa_puntos_recarga'),
    path('punto_recarga/<int:pk>/', PuntoRecargaDetailView.as_view(), name='detalle_punto_recarga'),
    path('iniciar-carga/', iniciar_carga_view, name='iniciar_carga'),
    
    # API endpoints
    path('api/puntos/', api_views.PuntoRecargaListAPIView.as_view(), name='api_puntos'),
    path('api/reservas/', api_views.ReservaListCreateAPIView.as_view(), name='api_reservas'),
    
    # Nuevos endpoints para la simulación de carga
    path('api/iniciar-carga/', api_views.IniciarCargaAPIView.as_view(), name='api_iniciar_carga'),
    path('api/detener-carga/', api_views.DetenerCargaAPIView.as_view(), name='api_detener_carga'),    
    path('api/estado-carga/<int:sesion_id>/', api_views.EstadoCargaAPIView.as_view(), name='api_estado_carga_detalle'),
    path('api/estado-carga/', api_views.EstadoCargaAPIView.as_view(), name='api_estado_carga_lista'),    
    path('api/sesiones-activas/', api_views.SesionesActivasAPIView.as_view(), name='api_sesiones_activas'),
    path('api/historial-sesiones/', api_views.HistorialSesionesAPIView.as_view(), name='api_historial_sesiones'),
    path('api/cancelar-reserva/', api_views.CancelarReservaAPIView.as_view(), name='api_cancelar_reserva'),
    path('api/puntos-en-uso/', api_views.PuntosEnUsoAPIView.as_view(), name='api_puntos_en_uso'),
    path('api/actualizar-bateria/', api_views.ActualizarBateriaAPIView.as_view(), name='api_actualizar_bateria'),
]
