from django.shortcuts import redirect
from django.conf import settings

class BlockDirectLoginAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo aplica a la ruta de login
        if request.path == settings.LOGIN_URL:
            referer = request.META.get('HTTP_REFERER', '')
            # Si no hay referer o no es de tu dominio, redirige (puedes cambiar la URL de destino)
            if not referer or not referer.startswith(request.build_absolute_uri('/')):
                return redirect('home')  # Cambia 'home' por la vista que prefieras
        return self.get_response(request)
