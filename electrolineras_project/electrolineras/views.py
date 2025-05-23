# electrolineras/views.py
from django.shortcuts import render
from django.views.generic import DetailView
from .models import PuntoRecarga, Reserva
from django.utils import timezone
from django.contrib.auth.decorators import login_required

class PuntoRecargaDetailView(DetailView):
    model = PuntoRecarga
    template_name = 'electrolineras/detalle_estacion_seg.html'  # Usando el template existente
    context_object_name = 'punto_recarga'

def mapa_puntos_recarga(request):
    print("========== FUNCIÓN MAPA_PUNTOS_RECARGA LLAMADA ==========")
    
    # Limpiar reservas expiradas y actualizar estados de puntos
    from .models import Reserva
    puntos_actualizados = Reserva.limpiar_reservas_expiradas()
    if puntos_actualizados > 0:
        print(f"Se actualizaron {puntos_actualizados} puntos que tenían reservas expiradas")
    
    puntos = PuntoRecarga.objects.all()
    # Debug: imprime en consola cuántos puntos hay y sus coordenadas
    print("Total puntos:", puntos.count())
    for p in puntos:
        print(f"Punto: {p.nombre}, Lat: {p.latitud}, Lon: {p.longitud}, Estado: {p.estado}")
    
    if puntos.exists():
        try:
            centro_lat = float(str(puntos[0].latitud).replace(',', '.'))
            centro_lon = float(str(puntos[0].longitud).replace(',', '.'))
        except Exception as e:
            print("Error al convertir coordenadas:", e)
            centro_lat = 36.7213
            centro_lon = -4.4214
    else:
        centro_lat = 36.7213  # Málaga por defecto
        centro_lon = -4.4214
    
    return render(request, 'electrolineras/mapa.html', {
        'puntos': puntos,
        'centro_lat': centro_lat,
        'centro_lon': centro_lon,
    })

@login_required
def iniciar_carga_view(request):
    """
    Vista para la página de iniciar carga.
    Muestra la reserva activa del usuario y permite iniciar una sesión de carga.
    """
    # Buscar la reserva activa del usuario
    reserva = Reserva.objects.filter(
        usuario=request.user, 
        fecha_expiracion__gt=timezone.now()
    ).first()
    
    return render(request, 'electrolineras/iniciar_carga.html', {
        'reserva': reserva
    })
