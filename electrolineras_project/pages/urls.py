from django.urls import path
from .views import PageListView, PageDetailView, PageCreate, PageUpdate, PageDelete

app_name = 'pages_app'  # Cambiado para evitar conflicto de namespace

urlpatterns = [
    # First list fixed URL patterns (most specific)
    path('create/', PageCreate.as_view(), name='create'),
    path('update/<int:pk>/', PageUpdate.as_view(), name='update'),
    path('delete/<int:pk>/', PageDelete.as_view(), name='delete'),
    
    # Then list the more generic URL patterns
    path('', PageListView.as_view(), name='pages'),
    path('<int:page_id>/<slug:page_slug>/', PageDetailView.as_view(), name='page'),
]