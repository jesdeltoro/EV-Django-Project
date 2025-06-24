# 📋 Guía para Actualizar la Información del Chatbot

## 🎯 Resumen
Tu chatbot ahora puede obtener información actualizada de **DOS FUENTES**:

1. **Base de datos Django** (Recomendado) - Panel de administración
2. **Archivo JSON** - Para información estática

---

## 🔧 Método 1: Panel de Administración Django (RECOMENDADO)

### ✅ Acceder al Panel
1. Ve a: `http://localhost:8000/admin/`
2. Inicia sesión con tu usuario administrador
3. Busca la sección **"CHATBOT"**
4. Haz clic en **"Configuración del Chatbot"**

### 💰 Actualizar Precios
- **Precio base por kWh**: Cambia de 0.300 a cualquier valor (ej: 0.350)
- **Descuento Premium**: Ajusta el descuento para usuarios Premium
- Los cambios se aplican **inmediatamente** al chatbot

### 📝 Actualizar Información General
- **Nombre del creador**: Cambiar si es necesario
- **Email de contacto**: julio@juliomalaga.me
- **Nombre de la app**: EvEMaps
- **Promoción activa**: Agregar mensajes promocionales temporales

### 🚀 Aplicar Cambios
- Los cambios se guardan automáticamente
- **No necesitas reiniciar el servidor**
- El chatbot usará la información actualizada en la siguiente conversación

---

## 🔧 Método 2: Archivo JSON (Para Información Estática)

### 📁 Ubicación del archivo
```
electrolineras_project/chatbot/knowledge_base.json
```

### 📝 Ejemplo de actualización
```json
{
  "precios": {
    "kwh_base": 0.35,     ← CAMBIAR AQUÍ EL PRECIO
    "moneda": "€",
    "descuento_premium": 0.05,
    "ultima_actualizacion": "2025-06-24"
  },
  "ubicaciones": [
    {
      "nombre": "Nueva Estación Sur",  ← AGREGAR NUEVAS UBICACIONES
      "direccion": "Calle Nueva 789",
      "conectores": ["Type 2", "CCS"],
      "potencias": [22, 50],
      "disponible_24_7": true
    }
  ]
}
```

---

## 🎯 Recomendaciones

### ✅ Para cambios frecuentes (precios, promociones):
- **Usa el Panel de Administración Django**
- Es más fácil y seguro
- No requiere editar código
- Cambios inmediatos

### ✅ Para información estática (conectores, servicios):
- **Usa el archivo JSON**
- Para información que cambia raramente
- Mantén una copia de respaldo

---

## 🔄 Comandos Útiles

### Crear configuración inicial:
```bash
python manage.py setup_chatbot
```

### Verificar configuración actual:
```bash
python manage.py shell
>>> from chatbot.models import ChatbotKnowledge
>>> config = ChatbotKnowledge.objects.first()
>>> print(f"Precio actual: {config.precio_kwh_base}€/kWh")
```

---

## 🚨 ¿Qué información actualizar regularmente?

### 📈 Mensualmente:
- **Precios del kWh**
- **Promociones activas**
- **Nuevas ubicaciones**

### 📅 Ocasionalmente:
- **Información de contacto**
- **Tipos de conectores disponibles**
- **Potencias de carga**

---

## 🐛 Resolución de Problemas

### ❌ Los cambios no se reflejan:
1. Verifica que la configuración esté marcada como "Activo"
2. Inicia una nueva conversación en el chat
3. Si persiste, reinicia el servidor Django

### ❌ Error en el panel de administración:
1. Verifica que hayas ejecutado las migraciones
2. Asegúrate de tener permisos de administrador

---

## 🤖 Manejo Inteligente de "No lo sé"

### ✅ Mejoras implementadas:
- **Errores técnicos claros**: Distingue entre problemas del servidor y falta de información
- **Respuestas profesionales**: En lugar de "Error", dice "No tengo esa información específica"
- **Guía para actualizaciones**: Te indica exactamente qué información necesita

### 📝 Ejemplos de respuestas mejoradas:

#### ❌ Antes (error genérico):
> "Error al procesar la respuesta"

#### ✅ Ahora (profesional y útil):
> "No tengo esa información específica en mi base de datos. Te recomiendo contactar con julio@juliomalaga.me para obtener detalles actualizados sobre [tema específico]."

### 🔧 Tipos de errores ahora diferenciados:

1. **⚠️ Problema técnico con IA**: Cuando Ollama no responde
2. **⚠️ Servicio temporalmente no disponible**: Cuando no hay conexión
3. **❓ No tengo esa información**: Cuando la IA no conoce la respuesta específica

---

## 📱 Resultado Final

Cuando actualices el precio a **0.35€/kWh**, el chatbot responderá:

> "💰 **Tarifas actuales de EV-EMAPs:**
> 
> 🔹 **Precio base:** 0.35 €/kWh
> 🔹 **Precio Premium:** 0.300 €/kWh (descuento de 0.05 €)
> 
> Las tarifas pueden variar según..."

¡**Tu chatbot ahora es completamente dinámico y fácil de actualizar!** 🎉
