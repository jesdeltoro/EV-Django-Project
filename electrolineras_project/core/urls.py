from django.urls import path
from .views import HomePageView, SamplePageView, MapaPageView

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('sample/', SamplePageView.as_view(), name="sample"),
    path('mapa/', MapaPageView.as_view(), name="mapa"),
]