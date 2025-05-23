from django.apps import AppConfig
import threading
import os
import time
from electrolineras.utils.estado_monitor import crear_monitor_estados


class ElectrolinerasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'electrolineras'
    
    def ready(self):
        # Evitar que se ejecute dos veces (Django llamará ready() dos veces en modo de desarrollo)
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
        
        # Iniciar el proceso de actualización de baterías en un hilo separado
        self.start_battery_updater()
        
        # Iniciar el monitor de estados inconsistentes
        self.start_estado_monitor()
    
    def start_estado_monitor(self):
        """Inicia el monitor de estados inconsistentes de puntos de recarga"""
        crear_monitor_estados()
    
    def start_battery_updater(self):
        """Inicia el proceso de actualización de baterías en segundo plano"""
        def updater_thread():
            from django.core import management
            from django.core.management import call_command
            
            print("✅ Iniciando actualizador automático de baterías")
            
            try:
                # Ejecutar el comando en un bucle infinito
                while True:
                    # Actualizar las baterías
                    from electrolineras.models import SesionCarga
                    sesiones = SesionCarga.objects.filter(activa=True)
                    for sesion in sesiones:
                        try:
                            bateria_anterior = sesion.porcentaje_bateria_actual
                            sesion.actualizar_bateria()
                            if sesion.porcentaje_bateria_actual > bateria_anterior:
                                print(f"✅ Batería actualizada: {bateria_anterior}% → {sesion.porcentaje_bateria_actual}%")
                        except Exception as e:
                            print(f"❌ Error al actualizar batería: {e}")
                    
                    # Esperar el intervalo especificado (30 segundos)
                    time.sleep(30)
            except Exception as e:
                print(f"❌ Error en el actualizador de baterías: {e}")
        
        # Iniciar el hilo
        thread = threading.Thread(target=updater_thread, daemon=True)
        thread.start()
