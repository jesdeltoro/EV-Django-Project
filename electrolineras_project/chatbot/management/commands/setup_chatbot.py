from django.core.management.base import BaseCommand
from chatbot.models import ChatbotKnowledge
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crea la configuración inicial del chatbot'

    def handle(self, *args, **options):
        if ChatbotKnowledge.objects.exists():
            self.stdout.write(
                self.style.WARNING('La configuración del chatbot ya existe.')
            )
            config = ChatbotKnowledge.objects.first()
            self.stdout.write(f'Precio actual: {config.precio_kwh_base}€/kWh')
        else:
            config = ChatbotKnowledge.objects.create(
                precio_kwh_base=Decimal('0.300'),
                descuento_premium=Decimal('0.050'),
                email_contacto='julio@juliomalaga.me',
                nombre_creador='Julio Schneider',
                app_nombre='EvEMaps',
                disponibilidad_24_7=True,
                activo=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Configuración del chatbot creada exitosamente!')
            )
            self.stdout.write(f'Precio configurado: {config.precio_kwh_base}€/kWh')
