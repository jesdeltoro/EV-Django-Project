from django.views.generic.base import TemplateView
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.http import HttpResponse
from django.views.decorators.http import require_GET

class HomePageView(TemplateView):
    template_name = "core/home.html"
#   def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['page_title'] = "Electrolineras"
#        context['page_description'] = "Electrolineras en España"
#        return context 
    
#    def get(self, request, *args, **kwargs):
#        return render(request, self.template_name, {'page_title': 'Electrolineras', 'page_description': 'Electrolineras en España'})

class SamplePageView(TemplateView):
    template_name = "core/sample.html"

class MapaPageView(TemplateView):
    template_name = "electrolineras/mapa.html"

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /api/",
        "Disallow: /chat/",
        "Disallow: /messenger/",
        "Disallow: /payments/",
        "Disallow: /profiles/",
        "Disallow: /download/",
        "Disallow: /electrolineras/api/",
        "Disallow: /electrolineras/iniciar-carga/",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


@require_GET
def google_site_verification(request):
    return HttpResponse(
        "google-site-verification: googleabf16e15cc4e6a49.html\n",
        content_type="text/html; charset=utf-8",
    )

@require_GET
def download_apk(request):
    """
    Vista para descargar el archivo APK de la aplicación EvEmaps.
    No requiere autenticación para permitir a cualquier usuario descargar la app.
    Adaptada para funcionar en la ruta específica de PythonAnywhere.
    """
    # Determinar si estamos en producción (PythonAnywhere) o en desarrollo local
    is_production = request.get_host() == 'evemaps.pythonanywhere.com'
    
    if is_production:
        # Ruta específica para PythonAnywhere
        file_path = '/home/evemaps/EV-Django-Project/electrolineras_project/media/downloads/app-release.apk'
    else:
        # Ruta para desarrollo local
        file_path = os.path.join(settings.MEDIA_ROOT, 'downloads', 'app-release.apk')
    
    if os.path.exists(file_path):
        try:
            # Crea la respuesta con el contenido del archivo
            response = FileResponse(open(file_path, 'rb'), content_type='application/vnd.android.package-archive')
            response['Content-Disposition'] = 'attachment; filename="EvEmaps.apk"'
            response['Content-Length'] = os.path.getsize(file_path)
            # Aseguramos que no se cachee la respuesta para siempre obtener la versión más reciente
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response
        except Exception as e:
            # Log del error pero sin mostrar detalles sensibles al usuario
            print(f"Error al servir el archivo APK: {str(e)}")
            raise Http404("Error al acceder al archivo APK.")
    else:
        raise Http404(f"El archivo APK no se encuentra disponible en este momento. Ruta buscada: {file_path}")
