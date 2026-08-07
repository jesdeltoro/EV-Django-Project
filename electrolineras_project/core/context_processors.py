from django.conf import settings


def seo_defaults(request):
    """Valores SEO comunes disponibles en todas las plantillas."""
    return {
        "SEO_SITE_NAME": "EvEMaps",
        "SEO_SITE_URL": settings.SITE_URL,
    }
