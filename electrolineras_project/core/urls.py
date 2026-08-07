from django.urls import path
from django.views.generic import RedirectView

from .views import (
    HomePageView,
    RegisterAPIView,
    download_apk,
    google_site_verification,
    robots_txt,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('mapa/', RedirectView.as_view(pattern_name='mapa_puntos_recarga', permanent=True), name="mapa"),
    path('robots.txt', robots_txt, name='robots_txt'),
    path(
        'googleabf16e15cc4e6a49.html',
        google_site_verification,
        name='google_site_verification',
    ),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('download/evemaps-app/', download_apk, name='download_apk'),
]
