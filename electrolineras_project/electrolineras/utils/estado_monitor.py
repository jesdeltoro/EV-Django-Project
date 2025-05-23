from django.apps import AppConfig
import threading
import time
from django.utils import timezone
import sys
import os

# Añadir el directorio del proyecto al PATH para poder importar django_types
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar funciones de ayuda para tipado
from django_types import with_id

class EstadosCheckThread(threading.Thread):
    """Thread para verificar y corregir estados inconsistentes de puntos de recarga."""
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.stop_event = threading.Event()
        
    def run(self):
        print("✅ Iniciando monitor de estados inconsistentes")
        while not self.stop_event.is_set():
            try:
                # Importar dentro del thread para evitar problemas de circular imports
                from electrolineras.models import PuntoRecarga, Reserva, SesionCarga
                
                # 1. Corregir puntos con reservas activas pero estado incorrecto
                reservas_activas = Reserva.objects.filter(fecha_expiracion__gt=timezone.now())
                puntos_corregidos = 0
                
                for reserva in reservas_activas:
                    punto = reserva.punto
                    punto_with_id = with_id(punto)
                    
                    # Si hay una sesión activa, el punto debería estar "en_uso"
                    if SesionCarga.objects.filter(punto_recarga=punto, activa=True).exists():
                        if punto.estado != 'en_uso':
                            punto.estado = 'en_uso'
                            punto.save()
                            puntos_corregidos += 1
                            print(f"Monitor de estados: Punto {punto_with_id.id} corregido a 'en_uso'")
                    # Si no hay sesión activa pero hay reserva, el punto debería estar "reservado"
                    elif punto.estado != 'reservado':
                        punto.estado = 'reservado'
                        punto.save()
                        puntos_corregidos += 1
                        print(f"Monitor de estados: Punto {punto_with_id.id} corregido a 'reservado'")
                
                # 2. Verificar puntos marcados como reservados sin reserva activa
                puntos_reservados = PuntoRecarga.objects.filter(estado='reservado')
                for punto in puntos_reservados:
                    punto_with_id = with_id(punto)
                    if not Reserva.objects.filter(punto=punto, fecha_expiracion__gt=timezone.now()).exists():
                        # No hay reserva activa, así que el punto debería estar disponible
                        punto.estado = 'disponible'
                        punto.save()
                        puntos_corregidos += 1
                        print(f"Monitor de estados: Punto {punto_with_id.pk} corregido a 'disponible'")
                
                # 3. Verificar puntos marcados como en uso sin sesión activa
                puntos_en_uso = PuntoRecarga.objects.filter(estado='en_uso')
                for punto in puntos_en_uso:
                    punto_with_id = with_id(punto)
                    if not SesionCarga.objects.filter(punto_recarga=punto, activa=True).exists():
                        # No hay sesión activa, así que el punto debería estar disponible
                        # A menos que tenga una reserva activa
                        if Reserva.objects.filter(punto=punto, fecha_expiracion__gt=timezone.now()).exists():
                            punto.estado = 'reservado'
                        else:
                            punto.estado = 'disponible'
                        punto.save()
                        puntos_corregidos += 1
                        print(f"Monitor de estados: Punto {punto_with_id.pk} corregido de 'en_uso' a '{punto.estado}'")
                
                if puntos_corregidos > 0:
                    print(f"Monitor de estados: {puntos_corregidos} puntos corregidos en total")
                
                # 4. Limpiar reservas expiradas
                Reserva.limpiar_reservas_expiradas()
                
            except Exception as e:
                print(f"Error en monitor de estados: {e}")
            
            # Dormir 10 segundos antes de la próxima verificación (reducido para mayor frecuencia)
            time.sleep(10)

def crear_monitor_estados():
    """Crea e inicia el thread para monitorizar estados inconsistentes."""
    monitor = EstadosCheckThread()
    monitor.start()
    return monitor
