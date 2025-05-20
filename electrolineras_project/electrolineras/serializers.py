from rest_framework import serializers
from .models import PuntoRecarga, Reserva

class PuntoRecargaSerializer(serializers.ModelSerializer):
    reservado = serializers.SerializerMethodField()
    reservado_por = serializers.SerializerMethodField()
    fecha_expiracion = serializers.SerializerMethodField()

    class Meta:
        model = PuntoRecarga
        fields = '__all__'
        extra_fields = ['reservado', 'reservado_por', 'fecha_expiracion']

    def get_reservado(self, obj):
        from django.utils import timezone
        return Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).exists()

    def get_reservado_por(self, obj):
        from django.utils import timezone
        reserva = Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).first()
        if reserva:
            return reserva.usuario.username
        return None

    def get_fecha_expiracion(self, obj):
        from django.utils import timezone
        reserva = Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).first()
        if reserva:
            return reserva.fecha_expiracion
        return None

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ('usuario', 'fecha_inicio', 'fecha_expiracion')
