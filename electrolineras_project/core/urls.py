from django.urls import path, include
from .views import HomePageView, SamplePageView, MapaPageView

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('mapa/', MapaPageView.as_view(), name="mapa"),
    
    # Add a URL pattern for "pages" (blog section)
    path('pages/', include('pages.urls')),  # This includes all URLs from the pages app
]