from rest_framework import serializers
from .models import PuntoRecarga, Reserva, SesionCarga
from django.utils import timezone

class PuntoRecargaSerializer(serializers.ModelSerializer):
    reservado = serializers.SerializerMethodField()
    reservado_por = serializers.SerializerMethodField()
    fecha_expiracion = serializers.SerializerMethodField()
    tipo_conector_nombre = serializers.SerializerMethodField()
    sesion_actual = serializers.SerializerMethodField()
    reserva_id = serializers.SerializerMethodField()
    tiempo_restante = serializers.SerializerMethodField()
    es_reserva_usuario_actual = serializers.SerializerMethodField()  # New field

    class Meta:
        model = PuntoRecarga
        fields = (
            "id", "nombre", "direccion", "latitud", "longitud", 
            "potencia_kw", "tipo_conector", "tipo_conector_nombre",
            "reservado", "reservado_por", "fecha_expiracion", "reserva_id",
            "estado", "energia_suministrada_total", "energia_actual_sesion",
            "sesion_actual", "tiempo_restante", "es_reserva_usuario_actual"  # Include new field
        )
    
    def get_tipo_conector_nombre(self, obj):
        if obj.tipo_conector:
            return obj.tipo_conector.denominacion
        return None

    def get_reservado(self, obj):
        from django.utils import timezone
        return Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).exists()

    def get_reservado_por(self, obj):
        from django.utils import timezone
        reserva = Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).first()
        if reserva:
            return reserva.usuario.username
        return None

    def get_fecha_expiracion(self, obj):
        from django.utils import timezone
        reserva = Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).first()
        if reserva:
            return reserva.fecha_expiracion
        return None
    def get_sesion_actual(self, obj):
        """Devuelve información sobre la sesión de carga activa, si existe"""
        sesion = SesionCarga.objects.filter(punto_recarga=obj, activa=True).first()
        if sesion:
            # Calcular el costo estimado usando la tarifa actual
            costo_sin_iva = 0
            try:
                from payments.models import TarifaEnergia
                tarifa = TarifaEnergia.get_tarifa_actual()
                if tarifa:
                    costo_sin_iva = float(sesion.energia_consumida) * float(tarifa.precio_por_kwh)
            except Exception:
                # Si hay un error, usar un precio por defecto de 0.3€ por kWh
                costo_sin_iva = sesion.energia_consumida * 0.3
            
            # Calcular costo con IVA (21%)
            costo_con_iva = costo_sin_iva * 1.21
            
            return {
                "id": str(sesion.pk),  # Usar pk en lugar de id y convertir a string para evitar errores
                "porcentaje_bateria": sesion.porcentaje_bateria_actual,
                "energia_consumida": sesion.energia_consumida,
                "tiempo_activa": (timezone.now() - sesion.inicio).total_seconds() // 60,
                "usuario": sesion.usuario.username,  # Nombre de usuario para verificar permisos
                "costo_sin_iva": round(costo_sin_iva, 2),  # Costo sin IVA redondeado a 2 decimales
                "costo_con_iva": round(costo_con_iva, 2)   # Costo con IVA redondeado a 2 decimales
            }
        return None

    def get_reserva_id(self, obj):
        from django.utils import timezone
        reserva = Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).first()
        if reserva:
            return str(reserva.pk)  # Usar pk en lugar de id y convertir a string para evitar errores
        return None

    def get_tiempo_restante(self, obj):
        from django.utils import timezone
        reserva = Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).first()
        if reserva:
            tiempo_restante = (reserva.fecha_expiracion - timezone.now()).total_seconds()
            minutos_restantes = int(tiempo_restante // 60)
            segundos_restantes = int(tiempo_restante % 60)
            return f"{minutos_restantes}:{segundos_restantes:02d}"
        return None

    def get_es_reserva_usuario_actual(self, obj):
        from django.utils import timezone
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            reserva = Reserva.objects.filter(punto=obj, fecha_expiracion__gt=timezone.now()).first()
            if reserva:
                return reserva.usuario == request.user
        return False

class ReservaSerializer(serializers.ModelSerializer):
    punto_nombre = serializers.CharField(source="punto.nombre", read_only=True)

    class Meta:
        model = Reserva
        fields = ("id", "usuario", "punto", "punto_nombre", "fecha_inicio", "fecha_expiracion")
        read_only_fields = ("usuario", "fecha_inicio", "fecha_expiracion")


class SesionCargaSerializer(serializers.ModelSerializer):
    punto_nombre = serializers.CharField(source="punto_recarga.nombre", read_only=True)
    potencia_kw = serializers.FloatField(source="punto_recarga.potencia_kw", read_only=True)
    tipo_conector = serializers.CharField(source="punto_recarga.tipo_conector.denominacion", read_only=True)
    tiempo_carga = serializers.SerializerMethodField()
    tiempo_restante_estimado = serializers.SerializerMethodField()
    username = serializers.CharField(source="usuario.username", read_only=True)
    costo_estimado = serializers.SerializerMethodField()
    factura_id = serializers.SerializerMethodField()
    
    class Meta:
        model = SesionCarga
        fields = ("id", "reserva", "punto_recarga", "punto_nombre", "usuario", "username", "inicio", 
                 "fin", "activa", "porcentaje_bateria_inicial", "porcentaje_bateria_actual", 
                 "energia_consumida", "potencia_kw", "tipo_conector", "tiempo_carga",
                 "tiempo_restante_estimado", "costo_estimado", "factura_id")
        read_only_fields = ("reserva", "punto_recarga", "usuario", "inicio", "fin", 
                           "porcentaje_bateria_inicial", "energia_consumida")

    def get_tiempo_carga(self, obj):
        """Calcula el tiempo de carga en minutos"""
        if obj.activa:
            tiempo = (timezone.now() - obj.inicio).total_seconds() / 60
        else:
            tiempo = (obj.fin - obj.inicio).total_seconds() / 60 if obj.fin else 0
        return round(tiempo, 1)
    
    def get_tiempo_restante_estimado(self, obj):
        """Calcula el tiempo restante estimado para llegar al 100% en minutos"""
        if not obj.activa or obj.porcentaje_bateria_actual >= 100:
            return 0
            
        # Calcular velocidad de carga en % por minuto
        tiempo_transcurrido = (timezone.now() - obj.inicio).total_seconds() / 60  # minutos
        if tiempo_transcurrido <= 0:
            return "Calculando..."
            
        incremento_bateria = obj.porcentaje_bateria_actual - obj.porcentaje_bateria_inicial
        
        # Si no ha habido incremento todavía, usar una velocidad estimada basada en la potencia
        if incremento_bateria <= 0:
            # Estimación para una batería estándar de 75kWh
            potencia = obj.punto_recarga.potencia_kw or 50  # kW
            # Con una batería de 75kWh, cada 1% representa 0.75kWh
            # Velocidad de carga en % por minuto = (potencia / 60) / 0.75
            velocidad_carga = (potencia / 60) / 0.75
        else:
            velocidad_carga = incremento_bateria / tiempo_transcurrido  # % por minuto
        
        # Calcular tiempo restante
        if velocidad_carga <= 0:
            return "Calculando..."
            
        porcentaje_restante = 100 - obj.porcentaje_bateria_actual
        tiempo_restante = porcentaje_restante / velocidad_carga  # minutos
        
        return round(tiempo_restante, 0)
        
    def get_costo_estimado(self, obj):
        """Calcula el costo estimado usando la tarifa actual"""
        try:
            from payments.models import TarifaEnergia
            tarifa = TarifaEnergia.get_tarifa_actual()
            if tarifa:
                return round(float(obj.energia_consumida) * float(tarifa.precio_por_kwh), 2)
        except Exception:
            # Si hay un error, usar un precio por defecto de 0.3€ por kWh
            return round(obj.energia_consumida * 0.3, 2)
            
    def get_factura_id(self, obj):
        """Obtiene el ID de la factura asociada a la sesión de carga, si existe"""
        try:
            factura = getattr(obj, 'factura', None)
            if factura and factura.estado == 'pendiente':
                return factura.id
        except Exception:
            pass
        return None
