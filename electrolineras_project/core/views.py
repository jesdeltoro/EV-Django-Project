from django.views.generic.base import TemplateView
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer

class HomePageView(TemplateView):
    template_name = "core/home.html"
#   def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['page_title'] = "Electrolineras"
#        context['page_description'] = "Electrolineras en España"
#        return context 
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'page_title': 'Electrolineras', 'page_description': 'Electrolineras en España'})

class SamplePageView(TemplateView):
    template_name = "core/sample.html"

class MapaPageView(TemplateView):
    template_name = "electrolineras/mapa.html"

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]