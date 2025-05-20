from django.urls import path, include
from .views import HomePageView, SamplePageView, MapaPageView, RegisterAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('mapa/', MapaPageView.as_view(), name="mapa"),
    path('pages/', include('pages.urls')),  # This includes all URLs from the pages app
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
]