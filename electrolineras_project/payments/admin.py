from django.contrib import admin
from .models import TarifaEnergia, MetodoPago, Factura, Pago


@admin.register(TarifaEnergia)
class TarifaEnergiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_por_kwh', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('nombre',)
    ordering = ['-fecha_creacion']
    
    def save_model(self, request, obj, form, change):
        # Si esta tarifa se marca como activa, desactivar todas las demás
        if obj.activa:
            TarifaEnergia.objects.filter(activa=True).update(activa=False)
        super().save_model(request, obj, form, change)


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'ultimos_4_digitos', 'marca_tarjeta', 'activo', 'es_predeterminado')
    list_filter = ('tipo', 'activo', 'es_predeterminado', 'marca_tarjeta')
    search_fields = ('usuario__username', 'usuario__email', 'ultimos_4_digitos')
    ordering = ['-fecha_creacion']


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'usuario', 'total', 'estado', 'fecha_creacion', 'fecha_pago')
    list_filter = ('estado', 'fecha_creacion', 'fecha_pago')
    search_fields = ('numero_factura', 'usuario__username', 'usuario__email')
    readonly_fields = ('numero_factura', 'subtotal', 'impuestos', 'total', 'energia_consumida', 'precio_por_kwh')
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información General', {
            'fields': ('numero_factura', 'usuario', 'sesion_carga', 'estado')
        }),
        ('Detalles de Energía', {
            'fields': ('energia_consumida', 'precio_por_kwh', 'subtotal', 'impuestos', 'total')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_vencimiento', 'fecha_pago')
        }),
        ('Información de Pago', {
            'fields': ('stripe_payment_intent_id', 'metodo_pago_usado'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # No permitir crear facturas manualmente desde el admin
        return False


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'factura', 'usuario', 'cantidad', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('factura__numero_factura', 'usuario__username', 'stripe_payment_intent_id')
    readonly_fields = ('factura', 'usuario', 'cantidad', 'stripe_payment_intent_id', 'stripe_charge_id')
    ordering = ['-fecha_creacion']
    
    def has_add_permission(self, request):
        # No permitir crear pagos manualmente desde el admin
        return False
