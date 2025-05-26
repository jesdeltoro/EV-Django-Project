from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from payments.models import TarifaEnergia, MetodoPago


class Command(BaseCommand):
    help = 'Inicializa datos básicos para el sistema de pagos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--precio-kwh',
            type=float,
            default=0.30,
            help='Precio por kWh en EUR (por defecto: 0.30)'
        )
        parser.add_argument(
            '--nombre',
            type=str,
            default='Tarifa estándar de energía',
            help='Nombre de la tarifa'
        )
        parser.add_argument(
            '--descripcion',
            type=str,
            default='Tarifa inicial del sistema',
            help='Descripción de la tarifa'
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Fuerza la creación incluso si ya existe una tarifa'
        )

    def handle(self, *args, **options):
        precio_kwh = Decimal(str(options['precio_kwh']))
        descripcion = options['descripcion']
        forzar = options['forzar']

        # Verificar si ya existe una tarifa activa
        tarifa_existente = TarifaEnergia.objects.filter(activa=True).first()
        
        if tarifa_existente and not forzar:
            self.stdout.write(
                self.style.WARNING(
                    f'Ya existe una tarifa activa: {tarifa_existente.descripcion} '
                    f'({tarifa_existente.precio_por_kwh} EUR/kWh). '
                    'Use --forzar para crear una nueva.'
                )
            )
            return

        # Si se está forzando, desactivar tarifa existente
        if tarifa_existente and forzar:
            tarifa_existente.activa = False
            tarifa_existente.save()
            self.stdout.write(
                self.style.WARNING(
                    f'Tarifa anterior desactivada: {tarifa_existente.descripcion}'
                )
            )

        # Crear nueva tarifa
        nueva_tarifa = TarifaEnergia.objects.create(
            precio_por_kwh=precio_kwh,
            descripcion=descripcion,
            activa=True,
            fecha_inicio=timezone.now()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Tarifa creada exitosamente:\n'
                f'   - Descripción: {nueva_tarifa.descripcion}\n'
                f'   - Precio: {nueva_tarifa.precio_por_kwh} EUR/kWh\n'
                f'   - Fecha inicio: {nueva_tarifa.fecha_inicio}\n'
                f'   - ID: {nueva_tarifa.id}'
            )
        )

        # Mostrar estadísticas
        total_tarifas = TarifaEnergia.objects.count()
        tarifas_activas = TarifaEnergia.objects.filter(activa=True).count()
        
        self.stdout.write(
            self.style.HTTP_INFO(
                f'\n📊 Estadísticas del sistema:\n'
                f'   - Total de tarifas: {total_tarifas}\n'
                f'   - Tarifas activas: {tarifas_activas}'
            )
        )

        # Inicializar métodos de pago por defecto
        self.inicializar_metodos_pago()

    def inicializar_metodos_pago(self):
        metodos_pago = [
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
            ('paypal', 'PayPal'),
            ('transferencia', 'Transferencia Bancaria'),
        ]

        for tipo, descripcion in metodos_pago:
            MetodoPago.objects.get_or_create(
                tipo=tipo,
                defaults={'descripcion': descripcion}
            )

        self.stdout.write(
            self.style.SUCCESS('✅ Métodos de pago inicializados')
        )
