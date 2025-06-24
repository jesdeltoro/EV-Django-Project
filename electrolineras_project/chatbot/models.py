from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import json

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', null=True, blank=True)
    session_id = models.CharField(max_length=255, unique=True)  # Para usuarios no autenticados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Chat Session - {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        return f"Chat Session - Anónimo - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
        ('system', 'Sistema'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:30]}..."

    @staticmethod
    def get_chat_history(session_id, limit=10):
        """Obtener historial de chat para un ID de sesión específico"""
        session = ChatSession.objects.filter(session_id=session_id).first()
        if not session:
            return []
        
        # Usamos related_name='messages' para obtener los mensajes de esta sesión
        messages = Message.objects.filter(session=session).order_by('timestamp')[:limit]
        return [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
        
    @staticmethod
    def as_chatml(session_id):
        """Convertir mensajes a formato ChatML para APIs de LLM"""
        messages = Message.get_chat_history(session_id)
        if not messages:
            # Si no hay mensajes, devolvemos un mensaje de sistema inicial
            return [{"role": "system", "content": "Eres un asistente útil para usuarios de EV-EMAPs, una aplicación de electrolineras. Responde de forma amable y concisa."}]
        return messages

class ChatbotKnowledge(models.Model):
    """Modelo para gestionar la información del chatbot desde el admin"""
      # Precios
    precio_kwh_base = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        default=Decimal('0.300'),
        help_text="Precio base por kWh en euros"
    )
    descuento_premium = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        default=Decimal('0.050'),
        help_text="Descuento para usuarios Premium en euros"
    )
    
    # Información de contacto
    email_contacto = models.EmailField(default="julio@juliomalaga.me")
    nombre_creador = models.CharField(max_length=100, default="Julio Schneider")
    
    # Información de servicios
    app_nombre = models.CharField(max_length=50, default="EvEMaps")
    disponibilidad_24_7 = models.BooleanField(default=True)
    
    # Promociones
    promocion_activa = models.TextField(
        blank=True, 
        help_text="Texto de promoción actual (opcional)"
    )
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración del Chatbot"
        verbose_name_plural = "Configuración del Chatbot"
    
    def __str__(self):
        return f"Configuración - Precio: {self.precio_kwh_base}€/kWh"
    
    def save(self, *args, **kwargs):
        # Solo permitir una instancia
        if not self.pk and ChatbotKnowledge.objects.exists():
            raise ValueError('Solo puede existir una configuración del chatbot')
        return super().save(*args, **kwargs)
