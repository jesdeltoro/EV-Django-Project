from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_room, name='chat'),
    path('<str:room_name>/', views.chat_room, name='chat_room'),
]
