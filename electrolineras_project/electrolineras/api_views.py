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
    permission_classes = [permissions.IsAuthenticated]  # Cambiado de AllowAny a IsAuthenticated

class ReservaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  
        #return Reserva.objects.filter(usuario=self.request.user, fecha_expiracion__gt=timezone.now())
        return super().get_queryset().filter(usuario=self.request.user, fecha_expiracion__gt=timezone.now())

    def create(self, request, *args, **kwargs):
        # Verificar si el usuario ya tiene una reserva activa
        reserva_usuario = Reserva.objects.filter(usuario=request.user, fecha_expiracion__gt=timezone.now()).first()
        if reserva_usuario:
            # Obtener datos del punto de esta reserva
            punto_reservado = reserva_usuario.punto
            punto_serializer = PuntoRecargaSerializer(punto_reservado)
            
            # Calcular tiempo restante
            tiempo_restante = (reserva_usuario.fecha_expiracion - timezone.now()).total_seconds()
            minutos_restantes = int(tiempo_restante // 60)
            segundos_restantes = int(tiempo_restante % 60)
            
            return Response({
                'detail': 'Ya tienes una reserva activa.',
                'reserva_actual': {
                    'punto': punto_serializer.data,
                    'tiempo_restante': f"{minutos_restantes}:{segundos_restantes:02d}",
                    'fecha_expiracion': reserva_usuario.fecha_expiracion
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        punto_id = request.data.get('punto')
        if not punto_id:
            return Response({'detail': 'El campo "punto" es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el punto existe
        try:
            punto = PuntoRecarga.objects.get(id=punto_id)
        except PuntoRecarga.DoesNotExist:
            return Response({'detail': f'No existe un punto de recarga con ID {punto_id}.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el punto está reservado por otro usuario
        reserva_existente = Reserva.objects.filter(punto=punto, fecha_expiracion__gt=timezone.now()).first()
        if reserva_existente:
            punto_serializer = PuntoRecargaSerializer(punto)
            
            # Calcular tiempo restante
            tiempo_restante = (reserva_existente.fecha_expiracion - timezone.now()).total_seconds()
            minutos_restantes = int(tiempo_restante // 60)
            segundos_restantes = int(tiempo_restante % 60)
            
            return Response({
                'detail': 'Este punto ya está reservado.',
                'punto_reservado': punto_serializer.data,
                'reservado_por': reserva_existente.usuario.username,
                'tiempo_restante': f"{minutos_restantes}:{segundos_restantes:02d}",
                'fecha_expiracion': reserva_existente.fecha_expiracion
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear la reserva si todo está bien
        reserva = Reserva.objects.create(
            usuario=request.user,
            punto=punto,
            fecha_inicio=timezone.now(),
            fecha_expiracion=timezone.now() + timezone.timedelta(minutes=30)
        )
        serializer = self.get_serializer(reserva)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
