from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from payments.models import TarifaEnergia


class Command(BaseCommand):
    help = 'Gestiona las tarifas de energía del sistema'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='accion', help='Acciones disponibles')
        
        # Subcomando para listar tarifas
        listar_parser = subparsers.add_parser('listar', help='Lista todas las tarifas')
        listar_parser.add_argument(
            '--activas-solo',
            action='store_true',
            help='Mostrar solo tarifas activas'
        )
        
        # Subcomando para crear tarifa
        crear_parser = subparsers.add_parser('crear', help='Crea una nueva tarifa')
        crear_parser.add_argument(
            'precio',
            type=float,
            help='Precio por kWh en USD'
        )
        crear_parser.add_argument(
            '--descripcion',
            type=str,
            default='Nueva tarifa de energía',
            help='Descripción de la tarifa'
        )
        crear_parser.add_argument(
            '--activar',
            action='store_true',
            help='Activar esta tarifa (desactiva las demás)'
        )
        
        # Subcomando para activar tarifa
        activar_parser = subparsers.add_parser('activar', help='Activa una tarifa específica')
        activar_parser.add_argument(
            'id',
            type=int,
            help='ID de la tarifa a activar'
        )
        
        # Subcomando para desactivar tarifa
        desactivar_parser = subparsers.add_parser('desactivar', help='Desactiva una tarifa específica')
        desactivar_parser.add_argument(
            'id',
            type=int,
            help='ID de la tarifa a desactivar'
        )

    def handle(self, *args, **options):
        accion = options.get('accion')
        
        if accion == 'listar':
            self.listar_tarifas(options)
        elif accion == 'crear':
            self.crear_tarifa(options)
        elif accion == 'activar':
            self.activar_tarifa(options)
        elif accion == 'desactivar':
            self.desactivar_tarifa(options)
        else:
            self.print_help('manage.py', 'gestionar_tarifas')

    def listar_tarifas(self, options):
        """Lista todas las tarifas del sistema"""
        if options['activas_solo']:
            tarifas = TarifaEnergia.objects.filter(activa=True)
            titulo = "📋 TARIFAS ACTIVAS"
        else:
            tarifas = TarifaEnergia.objects.all()
            titulo = "📋 TODAS LAS TARIFAS"
        
        self.stdout.write(self.style.HTTP_INFO(titulo))
        self.stdout.write(self.style.HTTP_INFO("=" * 50))
        
        if not tarifas.exists():
            self.stdout.write(self.style.WARNING("No hay tarifas registradas."))
            return
        
        for tarifa in tarifas.order_by('-fecha_inicio'):
            estado = "🟢 ACTIVA" if tarifa.activa else "🔴 INACTIVA"
            fecha_fin = tarifa.fecha_fin.strftime('%Y-%m-%d %H:%M') if tarifa.fecha_fin else "N/A"
            fecha_inicio = tarifa.fecha_inicio.strftime('%Y-%m-%d %H:%M') if tarifa.fecha_inicio else "N/A"
            
            self.stdout.write(
                f"\n🏷️  ID: {tarifa.id} | {estado}\n"
                f"   📝 Descripción: {tarifa.descripcion}\n"
                f"   💰 Precio: {tarifa.precio_por_kwh} USD/kWh\n"
                f"   📅 Inicio: {fecha_inicio}\n"
                f"   📅 Fin: {fecha_fin}"
            )
        
        # Estadísticas
        total = TarifaEnergia.objects.count()
        activas = TarifaEnergia.objects.filter(activa=True).count()
        self.stdout.write(
            self.style.HTTP_INFO(
                f"\n📊 Total: {total} tarifas | Activas: {activas}"
            )
        )

    def crear_tarifa(self, options):
        """Crea una nueva tarifa"""
        precio = Decimal(str(options['precio']))
        descripcion = options['descripcion']
        activar = options['activar']
        
        # Si se va a activar, desactivar otras tarifas
        if activar:
            TarifaEnergia.objects.filter(activa=True).update(
                activa=False,
                fecha_fin=timezone.now()
            )
        
        # Crear nueva tarifa
        nueva_tarifa = TarifaEnergia.objects.create(
            precio_por_kwh=precio,
            descripcion=descripcion,
            activa=activar,
            fecha_inicio=timezone.now()
        )
        
        estado = "y activada" if activar else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Tarifa creada {estado} exitosamente:\n"
                f"   - ID: {nueva_tarifa.id}\n"
                f"   - Descripción: {nueva_tarifa.descripcion}\n"
                f"   - Precio: {nueva_tarifa.precio_por_kwh} USD/kWh"
            )
        )

    def activar_tarifa(self, options):
        """Activa una tarifa específica"""
        tarifa_id = options['id']
        
        try:
            tarifa = TarifaEnergia.objects.get(id=tarifa_id)
        except TarifaEnergia.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ No existe una tarifa con ID {tarifa_id}")
            )
            return
        
        if tarifa.activa:
            self.stdout.write(
                self.style.WARNING(f"⚠️  La tarifa {tarifa_id} ya está activa")
            )
            return
        
        # Desactivar otras tarifas
        TarifaEnergia.objects.filter(activa=True).update(
            activa=False,
            fecha_fin=timezone.now()
        )
        
        # Activar la tarifa seleccionada
        tarifa.activa = True
        tarifa.fecha_fin = None
        tarifa.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Tarifa {tarifa_id} activada exitosamente:\n"
                f"   - Descripción: {tarifa.descripcion}\n"
                f"   - Precio: {tarifa.precio_por_kwh} USD/kWh"
            )
        )

    def desactivar_tarifa(self, options):
        """Desactiva una tarifa específica"""
        tarifa_id = options['id']
        
        try:
            tarifa = TarifaEnergia.objects.get(id=tarifa_id)
        except TarifaEnergia.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ No existe una tarifa con ID {tarifa_id}")
            )
            return
        
        if not tarifa.activa:
            self.stdout.write(
                self.style.WARNING(f"⚠️  La tarifa {tarifa_id} ya está inactiva")
            )
            return
        
        # Desactivar la tarifa
        tarifa.activa = False
        tarifa.fecha_fin = timezone.now()
        tarifa.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Tarifa {tarifa_id} desactivada exitosamente"
            )
        )
        
        # Advertir si no quedan tarifas activas
        activas = TarifaEnergia.objects.filter(activa=True).count()
        if activas == 0:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  ADVERTENCIA: No hay tarifas activas. "
                    "Los pagos automáticos pueden fallar."
                )
            )
