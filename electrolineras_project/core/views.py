from django.views.generic.base import TemplateView
from django.shortcuts import render

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