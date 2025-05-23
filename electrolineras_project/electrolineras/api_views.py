from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import PuntoRecarga, Reserva, SesionCarga
from .serializers import PuntoRecargaSerializer, ReservaSerializer, SesionCargaSerializer
from typing import Any, Optional, List, cast, Dict
from django.db.models.query import QuerySet
from django.db.models import Model
import random

# Eliminamos toda la parte de tipado que estaba causando problemas

class PuntoRecargaListAPIView(generics.ListAPIView):
    queryset = PuntoRecarga.objects.all()
    serializer_class = PuntoRecargaSerializer
    permission_classes = [permissions.IsAuthenticated]  # Cambiado de AllowAny a IsAuthenticated

class ReservaListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reservas = Reserva.objects.filter(
            usuario=request.user, 
            fecha_expiracion__gt=timezone.now()
        )
        serializer = ReservaSerializer(reservas, many=True)
        return Response(serializer.data)
    def post(self, request):
        # Verificar si el usuario ya tiene una sesión de carga activa
        sesion_activa = SesionCarga.objects.filter(usuario=request.user, activa=True).first()
        if sesion_activa:
            punto_actual = sesion_activa.punto_recarga
            return Response({
                'detail': f'Ya tienes una sesión de carga activa en el punto {punto_actual.nombre}. Debes terminar esa carga antes de crear una nueva reserva.',
                'sesion_actual': {
                    'id': str(sesion_activa.pk),
                    'punto_nombre': punto_actual.nombre,
                    'direccion': punto_actual.direccion
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        # Crear la reserva
        reserva = Reserva.objects.create(
            usuario=request.user,
            punto=punto,
            fecha_inicio=timezone.now(),
            fecha_expiracion=timezone.now() + timezone.timedelta(minutes=30)
        )
        serializer = ReservaSerializer(reserva)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IniciarCargaAPIView(APIView):
    """
    Vista de API para iniciar una sesión de carga en un punto de recarga.
    Permite a un usuario iniciar la carga en un punto reservado.
    """
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        print(f"API IniciarCargaAPIView llamada por {request.user}") 
        print(f"Datos recibidos: {request.data}")
        
        # Obtener el ID de la reserva
        reserva_id = request.data.get('reserva_id')
        if not reserva_id:
            print("Error: No se proporcionó ID de reserva")
            return Response({'error': 'El ID de reserva es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verificar que la reserva existe, pertenece al usuario y está activa
            reserva = Reserva.objects.get(
                id=reserva_id, 
                usuario=request.user, 
                fecha_expiracion__gt=timezone.now()
            )
            print(f"Reserva encontrada: {reserva_id} para el punto {reserva.punto.nombre}")
        except Reserva.DoesNotExist:
            print(f"Error: Reserva no encontrada - ID: {reserva_id}, Usuario: {request.user}")
            return Response(
                {'error': 'Reserva no encontrada o expirada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
          # Verificar si ya existe una sesión activa para esta reserva
        sesion_existente = SesionCarga.objects.filter(reserva=reserva, activa=True).first()
        if sesion_existente:
            # Si ya existe una sesión, devolver esa sesión en lugar de crear una nueva
            serializer = SesionCargaSerializer(sesion_existente)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Verificar si el usuario ya tiene una sesión activa en cualquier otro punto
        otra_sesion_activa = SesionCarga.objects.filter(usuario=request.user, activa=True).first()
        if otra_sesion_activa:
            punto_actual = otra_sesion_activa.punto_recarga
            print(f"El usuario {request.user.username} ya tiene una carga activa en el punto {punto_actual.nombre}")
            return Response({
                'error': f'Ya tienes una carga activa en el punto {punto_actual.nombre}. Debes terminar esa carga antes de iniciar una nueva.',
                'sesion_actual': {
                    'id': str(otra_sesion_activa.pk),
                    'punto_nombre': punto_actual.nombre,
                    'direccion': punto_actual.direccion
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Verificar el estado del punto de recarga
        punto = reserva.punto
        
        # Si el punto está en uso, pero tú tienes la reserva, te permitimos iniciar la carga
        # Esto corrige problemas de estados inconsistentes en la base de datos
        if punto.estado == 'en_uso':
            print(f"Punto {punto.nombre} está marcado como en uso, verificando si podemos corregir esto")
            # Forzar la actualización del estado si no hay sesiones activas para este punto
            if not SesionCarga.objects.filter(punto_recarga=punto, activa=True).exists():
                print(f"No hay sesiones activas para este punto, restableciendo estado a disponible")
                punto.estado = 'disponible'
                punto.save()
            elif SesionCarga.objects.filter(reserva=reserva, activa=True).exists():
                # Si el usuario ya tiene una sesión activa para esta reserva
                sesion_existente = SesionCarga.objects.filter(reserva=reserva, activa=True).first()
                serializer = SesionCargaSerializer(sesion_existente)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # El punto realmente está en uso por otro usuario
                return Response(
                    {'error': 'Este punto de recarga ya está en uso por otro usuario'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
          # Crear sesión de carga con un porcentaje inicial de batería aleatorio
        bateria_inicial = random.randint(10, 30)  # Simular porcentaje inicial de batería
        try:
            print(f"Creando sesión de carga. Batería inicial: {bateria_inicial}%")
            sesion = SesionCarga.objects.create(
                reserva=reserva,
                punto_recarga=punto,
                usuario=request.user,
                porcentaje_bateria_inicial=bateria_inicial,
                porcentaje_bateria_actual=bateria_inicial
            )
            print(f"Sesión creada: {sesion}")
            sesion.iniciar_carga()
            print(f"Carga iniciada. Estado del punto: {punto.estado}")
            
            # Devolver la información de la sesión creada
            serializer = SesionCargaSerializer(sesion)
            print(f"Devolviendo datos: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            print(f"Error de validación al crear la sesión: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error al crear la sesión: {e}")
            return Response({'error': f'Error al crear la sesión: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetenerCargaAPIView(APIView):
    """
    Vista de API para detener una sesión de carga activa.
    Permite a un usuario detener la carga de su vehículo.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Obtener el ID de la sesión
        sesion_id = request.data.get('sesion_id')
        if not sesion_id:
            return Response({'error': 'El ID de sesión es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verificar que la sesión existe, pertenece al usuario y está activa
            sesion = SesionCarga.objects.get(
                id=sesion_id, 
                usuario=request.user, 
                activa=True
            )
        except SesionCarga.DoesNotExist:
            return Response(
                {'error': 'Sesión de carga no encontrada o ya finalizada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Asegurarnos de que la reserva asociada también se marca como expirada
        if hasattr(sesion, 'reserva') and sesion.reserva:
            sesion.reserva.fecha_expiracion = timezone.now()
            sesion.reserva.save(update_fields=['fecha_expiracion'])
        
        # Detener la sesión de carga
        sesion.detener_carga()
        
        # Devolver la información de la sesión finalizada
        serializer = SesionCargaSerializer(sesion)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EstadoCargaAPIView(APIView):
    """
    Vista de API para consultar el estado de una sesión de carga.
    Permite a un usuario obtener información en tiempo real sobre su sesión de carga.
    Ahora también simula el incremento del porcentaje de batería basado en el tiempo.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, sesion_id=None):
        if not sesion_id:
            # Si no se proporciona un ID, devolver todas las sesiones del usuario
            sesiones = SesionCarga.objects.filter(usuario=request.user)
            
            # Para cada sesión activa, actualizar el porcentaje de batería automáticamente
            for sesion in sesiones:
                if sesion.activa:
                    sesion.actualizar_bateria()
            
            serializer = SesionCargaSerializer(sesiones, many=True)
            return Response(serializer.data)
        
        try:
            # Obtener la sesión específica
            sesion = SesionCarga.objects.get(id=sesion_id)
            
            # Verificar que el usuario tiene acceso a esta sesión
            if sesion.usuario != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'No tienes permiso para ver esta sesión'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Actualizar automáticamente el porcentaje de batería si la sesión está activa
            if sesion.activa:
                sesion.actualizar_bateria()
                
            serializer = SesionCargaSerializer(sesion)
            return Response(serializer.data)
        except SesionCarga.DoesNotExist:
            return Response(
                {'error': 'Sesión de carga no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class SesionesActivasAPIView(APIView):
    """
    Vista de API para listar todas las sesiones de carga activas del usuario.
    Ahora también actualiza automáticamente el porcentaje de batería.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        sesiones = SesionCarga.objects.filter(
            usuario=request.user,
            activa=True
        )
        
        # Actualizar automáticamente el porcentaje de batería de todas las sesiones activas
        for sesion in sesiones:
            sesion.actualizar_bateria()
            
        serializer = SesionCargaSerializer(sesiones, many=True)
        return Response(serializer.data)


class HistorialSesionesAPIView(APIView):
    """
    Vista de API para listar el historial de sesiones de carga de un usuario.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        sesiones = SesionCarga.objects.filter(
            usuario=request.user,
            activa=False
        ).order_by('-inicio')
        serializer = SesionCargaSerializer(sesiones, many=True)
        return Response(serializer.data)


class CancelarReservaAPIView(APIView):
    """
    Vista de API para cancelar una reserva activa.
    Permite a un usuario cancelar una reserva antes de que expire.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Obtener el ID de la reserva
        reserva_id = request.data.get('reserva_id')
        if not reserva_id:
            return Response({'error': 'El ID de reserva es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verificar que la reserva existe, pertenece al usuario y está activa
            reserva = Reserva.objects.get(
                id=reserva_id, 
                usuario=request.user, 
                fecha_expiracion__gt=timezone.now()
            )
            
            # Verificar que no hay sesiones de carga activas para esta reserva
            if SesionCarga.objects.filter(reserva=reserva, activa=True).exists():
                return Response(
                    {'error': 'No se puede cancelar una reserva con una sesión de carga activa. Detén la carga primero.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
              # Actualizar el estado del punto a disponible si estaba reservado
            punto = reserva.punto
            if punto.estado == 'reservado':
                punto.estado = 'disponible'
                punto.save()
            
            # Marcar la reserva como expirada
            reserva.fecha_expiracion = timezone.now()
            reserva.save()
            
            return Response({'success': f'Reserva {reserva_id} cancelada correctamente'}, status=status.HTTP_200_OK)
            
        except Reserva.DoesNotExist:
            return Response(
                {'error': 'Reserva no encontrada o ya expirada'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class PuntosEnUsoAPIView(APIView):
    """
    Vista de API para listar todos los puntos de recarga que están en uso,
    junto con los detalles de la sesión de carga y el usuario que lo está utilizando.
    Ahora actualiza automáticamente el porcentaje de batería.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Obtener todos los puntos en uso
        puntos_en_uso = PuntoRecarga.objects.filter(estado='en_uso')
        
        # Preparar los datos de respuesta
        resultado = []
        
        for punto in puntos_en_uso:
            # Buscar la sesión activa para este punto
            try:
                sesion = SesionCarga.objects.get(punto_recarga=punto, activa=True)
                
                # Actualizar la batería automáticamente
                sesion.actualizar_bateria()
                
                # Obtener datos del usuario
                usuario = sesion.usuario
                  # Añadir a la respuesta
                punto_data = PuntoRecargaSerializer(punto).data
                punto_data['sesion'] = {
                    'id': str(sesion.pk),
                    'usuario': usuario.username,
                    'inicio': sesion.inicio,
                    'porcentaje_bateria_actual': sesion.porcentaje_bateria_actual,
                    'energia_consumida': sesion.energia_consumida
                }
                resultado.append(punto_data)
            except SesionCarga.DoesNotExist:
                # Este punto está marcado como en uso pero no tiene una sesión activa
                # Esto podría indicar una inconsistencia en la base de datos
                punto_data = PuntoRecargaSerializer(punto).data
                punto_data['estado_inconsistente'] = True
                punto_data['mensaje'] = "Punto marcado como en uso pero sin sesión activa asociada"
                resultado.append(punto_data)
        
        return Response(resultado)

class ActualizarBateriaAPIView(APIView):
    """
    Vista de API para actualizar manualmente el porcentaje de batería de una sesión de carga.
    Permite a un usuario forzar una actualización en el porcentaje de batería de su sesión.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Obtener el ID de la sesión
        sesion_id = request.data.get('sesion_id')
        if not sesion_id:
            return Response({'error': 'El ID de sesión es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verificar que la sesión existe, pertenece al usuario y está activa
            sesion = SesionCarga.objects.get(
                id=sesion_id, 
                usuario=request.user, 
                activa=True
            )
        except SesionCarga.DoesNotExist:
            return Response(
                {'error': 'Sesión de carga no encontrada o ya finalizada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Actualizar la batería (forzar actualización)
        porcentaje_actual, energia_consumida = sesion.actualizar_bateria(forzar_actualizacion=True)
        
        # Verificar si se ha llegado al 100% de batería
        if porcentaje_actual >= 100:
            # Opcionalmente, detener la carga automáticamente al llegar al 100%
            mensaje = "Batería al 100%. Se recomienda desconectar el vehículo."
        else:
            mensaje = f"Batería actualizada al {porcentaje_actual}%"
        
        return Response({
            'porcentaje_bateria': porcentaje_actual,
            'energia_consumida': energia_consumida,
            'mensaje': mensaje
        }, status=status.HTTP_200_OK)
