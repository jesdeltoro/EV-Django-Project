from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import PuntoRecarga, Reserva
from .serializers import PuntoRecargaSerializer, ReservaSerializer
from typing import Any
from django.db.models.query import QuerySet

class PuntoRecargaListAPIView(generics.ListAPIView):
    queryset = PuntoRecarga.objects.all()
    serializer_class = PuntoRecargaSerializer
    permission_classes = [permissions.AllowAny]

class ReservaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  
        return Reserva.objects.filter(usuario=self.request.user, fecha_expiracion__gt=timezone.now())

    def create(self, request, *args, **kwargs):
        # Solo una reserva activa por usuario
        if Reserva.objects.filter(usuario=request.user, fecha_expiracion__gt=timezone.now()).exists():
            return Response({'detail': 'Ya tienes una reserva activa.'}, status=status.HTTP_400_BAD_REQUEST)
        punto_id = request.data.get('punto')
        if Reserva.objects.filter(punto_id=punto_id, fecha_expiracion__gt=timezone.now()).exists():
            return Response({'detail': 'Este punto ya está reservado.'}, status=status.HTTP_400_BAD_REQUEST)
        reserva = Reserva.objects.create(
            usuario=request.user,
            punto_id=punto_id,
            fecha_inicio=timezone.now(),
            fecha_expiracion=timezone.now() + timezone.timedelta(minutes=30)
        )
        serializer = self.get_serializer(reserva)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
