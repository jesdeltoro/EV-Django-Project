from django.contrib import admin
from .models import ChatSession, Message, ChatbotKnowledge

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at', 'updated_at')
    list_filter = ('created_at', )
    search_fields = ('user__username', 'session_id')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'short_content', 'timestamp')
    list_filter = ('role', 'timestamp')
    search_fields = ('content', 'session__session_id')

    def short_content(self, obj):
        """Contenido"""  # Esta es otra forma de establecer short_description usando docstring
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['precio_kwh_base', 'descuento_premium', 'nombre_creador', 'activo', 'fecha_actualizacion']
    fieldsets = (
        ('Precios y Tarifas', {
            'fields': ('precio_kwh_base', 'descuento_premium')
        }),
        ('Información de Contacto', {
            'fields': ('nombre_creador', 'email_contacto')
        }),
        ('Servicios', {
            'fields': ('app_nombre', 'disponibilidad_24_7')
        }),
        ('Promociones', {
            'fields': ('promocion_activa',),
            'description': 'Mensaje promocional que aparecerá en las respuestas del chatbot'
        }),
        ('Control', {
            'fields': ('activo', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['fecha_actualizacion']
    
    def has_add_permission(self, request):
        # Solo permitir una instancia
        return not ChatbotKnowledge.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar la configuración
        return False
