from django.core.management.base import BaseCommand
from django.utils import timezone
from electrolineras.models import PuntoRecarga, SesionCarga, Reserva
import time
import random

class Command(BaseCommand):
    help = 'Simula el comportamiento de los puntos de recarga en tiempo real'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando simulación de puntos de recarga...'))
        
        try:
            while True:
                # Procesamos sesiones activas
                self.simular_sesiones_activas()
                
                # Actualizar estados de puntos con reservas que no tienen sesiones
                self.actualizar_puntos_reservados()
                
                # Actualizar puntos cuyas reservas han expirado
                self.actualizar_puntos_expirados()
                
                time.sleep(5)  # Actualizar cada 5 segundos
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Simulación detenida por el usuario'))

    def simular_sesiones_activas(self):
        """Simula la carga en sesiones activas"""
        sesiones_activas = SesionCarga.objects.filter(activa=True)
        
        for sesion in sesiones_activas:
            # Calcular incremento de batería basado en la potencia del punto
            incremento_bateria = min(2, (sesion.punto_recarga.potencia_kw or 7) / 50)
              # Incrementar batería
            if sesion.porcentaje_bateria_actual < 100:
                sesion.porcentaje_bateria_actual = int(min(100, sesion.porcentaje_bateria_actual + incremento_bateria))
                
                # Calcular energía consumida (kWh)
                tiempo_transcurrido = 5/3600  # 5 segundos en horas
                energia_consumida = (sesion.punto_recarga.potencia_kw or 7) * tiempo_transcurrido
                
                sesion.energia_consumida += energia_consumida
                sesion.punto_recarga.energia_actual_sesion += energia_consumida
                
                sesion.save()
                sesion.punto_recarga.save()
                
                self.stdout.write(f'Punto {sesion.punto_recarga.nombre}: {sesion.porcentaje_bateria_actual:.1f}% | Energía: {sesion.energia_consumida:.2f} kWh')
            else:
                # Batería llena, detener carga
                sesion.detener_carga()
                self.stdout.write(self.style.SUCCESS(f'Carga completa en {sesion.punto_recarga.nombre}'))

    def actualizar_puntos_reservados(self):
        """Actualiza el estado de los puntos que tienen reserva activa pero no sesión de carga"""
        # Obtener IDs de puntos con sesiones activas
        puntos_con_sesion = SesionCarga.objects.filter(activa=True).values_list('punto_recarga_id', flat=True)
        
        # Obtener reservas activas
        reservas_activas = Reserva.objects.filter(fecha_expiracion__gt=timezone.now())
        
        # Filtrar puntos con reserva activa pero sin sesión de carga
        for reserva in reservas_activas:
            if reserva.punto.id not in puntos_con_sesion and reserva.punto.estado == 'disponible':
                punto = reserva.punto
                punto.estado = 'reservado'
                punto.save()
                self.stdout.write(f'Punto {punto.nombre} marcado como reservado')

    def actualizar_puntos_expirados(self):
        """Libera los puntos cuyas reservas han expirado"""
        # Obtener puntos con estado reservado o en uso
        puntos_ocupados = PuntoRecarga.objects.filter(estado__in=['reservado', 'en_uso'])
        
        for punto in puntos_ocupados:
            # Verificar si hay sesión activa
            tiene_sesion_activa = SesionCarga.objects.filter(punto_recarga=punto, activa=True).exists()
            
            if tiene_sesion_activa:
                continue  # Si tiene sesión activa, no modificar estado
            
            # Verificar si tiene reserva activa
            tiene_reserva_activa = Reserva.objects.filter(
                punto=punto, 
                fecha_expiracion__gt=timezone.now()
            ).exists()
            
            if not tiene_reserva_activa:
                punto.estado = 'disponible'
                punto.save()
                self.stdout.write(f'Reserva expirada: Punto {punto.nombre} liberado')
