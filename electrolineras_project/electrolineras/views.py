# electrolineras/views.py
from django.shortcuts import render
from django.views.generic import DetailView
from .models import PuntoRecarga

class PuntoRecargaDetailView(DetailView):
    model = PuntoRecarga
    template_name = 'punto_recarga_detail.html'  # Asegúrate de que exista este template
    context_object_name = 'punto_recarga'

def mapa_puntos_recarga(request):
    print("========== FUNCIÓN MAPA_PUNTOS_RECARGA LLAMADA ==========")
    puntos = PuntoRecarga.objects.all()
    # Debug: imprime en consola cuántos puntos hay y sus coordenadas
    print("Total puntos:", puntos.count())
    for p in puntos:
        print("Punto:", p.nombre, "Lat:", p.latitud, "Lon:", p.longitud)
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
