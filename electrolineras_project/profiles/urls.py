from django.urls import path
from .views import ProfileListView, ProfileDetailView

urlpatterns = [
    path('', ProfileListView.as_view(), name='list'),
    path('<str:username>/', ProfileDetailView.as_view(), name='detail'),
]
