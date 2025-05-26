from django.core.management.base import BaseCommand
from django.utils import timezone
from electrolineras.models import SesionCarga
import time

class Command(BaseCommand):
    help = 'Actualiza automáticamente el porcentaje de batería de las sesiones activas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--intervalo',
            type=int,
            default=60,
            help='Intervalo en segundos para actualizar las baterías (por defecto: 60 segundos)'
        )

    def handle(self, *args, **options):
        intervalo = options['intervalo']
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando actualización automática de baterías cada {intervalo} segundos...')
        )
        
        try:
            while True:
                self.actualizar_baterias()
                time.sleep(intervalo)  # Actualizar según el intervalo especificado
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Proceso detenido por el usuario'))

    def actualizar_baterias(self):
        """Actualiza el porcentaje de batería de todas las sesiones activas"""
        sesiones_activas = SesionCarga.objects.filter(activa=True)
        self.stdout.write(f'Actualizando {sesiones_activas.count()} sesiones activas...')
        
        for sesion in sesiones_activas:
            # Actualizar la batería
            bateria_anterior = sesion.porcentaje_bateria_actual
            sesion.actualizar_bateria()
            
            # Mostrar información sobre la actualización
            if sesion.porcentaje_bateria_actual > bateria_anterior:
                # Calcular costo estimado usando la tarifa actual
                try:
                    from payments.models import TarifaEnergia
                    tarifa = TarifaEnergia.get_tarifa_actual()
                    costo_estimado = float(sesion.energia_consumida) * float(tarifa.precio_por_kwh)
                except:
                    costo_estimado = 0
                
                self.stdout.write(
                    f'Punto {sesion.punto_recarga.nombre}: Batería {bateria_anterior}% → {sesion.porcentaje_bateria_actual}% | '
                    f'Energía: {sesion.energia_consumida:.2f} kWh | '
                    f'Costo estimado: {costo_estimado:.2f}€ | '
                    f'Usuario: {sesion.usuario.username}'
                )
                
                # Si la batería llega al 100%, sugerir detener la carga
                if sesion.porcentaje_bateria_actual >= 100:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'🔋 Batería al 100% en {sesion.punto_recarga.nombre}. '
                            f'Se recomienda detener la carga. Costo final: {costo_estimado:.2f}€'
                        )
                    )
