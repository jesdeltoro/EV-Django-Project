from django.shortcuts import redirect
from django.conf import settings


class SeoHeadersMiddleware:
    """Evita que buscadores indexen zonas privadas, técnicas o transaccionales."""

    NOINDEX_PREFIXES = (
        "/admin/",
        "/accounts/",
        "/api/",
        "/chat/",
        "/messenger/",
        "/payments/",
        "/profiles/",
        "/download/",
        "/electrolineras/api/",
        "/electrolineras/iniciar-carga/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(self.NOINDEX_PREFIXES):
            response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response


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
