# electrolineras/admin.py
from django.contrib import admin
from .models import PuntoRecarga, Conector

admin.site.register(PuntoRecarga)
admin.site.register(Conector)