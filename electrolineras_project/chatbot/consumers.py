import json
import uuid
import asyncio
import httpx
import os
import re
from pathlib import Path
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .models import ChatSession, Message
from asgiref.sync import sync_to_async

OLLAMA_AVAILABLE = True  # ¡IA activada! Cambia a False si quieres desactivarla

# Función para cargar la base de conocimientos
def cargar_knowledge_base():
    """Carga la base de conocimientos desde el archivo JSON"""
    try:
        kb_path = Path(__file__).parent / 'knowledge_base.json'
        with open(kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "precios": {"kwh_base": 0.30, "moneda": "€"},
            "contacto": {"email": "julio@juliomalaga.me"}
        }

@sync_to_async
def cargar_knowledge_base_db():
    """Carga la configuración desde la base de datos"""
    from .models import ChatbotKnowledge
    try:
        config = ChatbotKnowledge.objects.filter(activo=True).first()
        if config:
            return {
                "precios": {
                    "kwh_base": float(config.precio_kwh_base),
                    "descuento_premium": float(config.descuento_premium),
                    "moneda": "€"
                },
                "contacto": {
                    "email": config.email_contacto,
                    "creador": config.nombre_creador
                },
                "servicios": {
                    "app_nombre": config.app_nombre,
                    "disponibilidad_24_7": config.disponibilidad_24_7,
                    "promocion": config.promocion_activa
                }
            }
        else:
            return cargar_knowledge_base()  # Fallback al archivo JSON
    except Exception:
        return cargar_knowledge_base()  # Fallback al archivo JSON

# Cargar knowledge base al inicio
KNOWLEDGE_BASE = cargar_knowledge_base()

# Lista de palabras censuradas (malsonantes y contenido inapropiado)
PALABRAS_CENSURADAS = [
    # Palabras malsonantes comunes en español
    'puta', 'puto', 'joder', 'jodido', 'cabrón', 'cabron', 'gilipollas', 'hijo de puta',
    'coño', 'cono', 'mierda', 'cagar', 'cagada', 'imbécil', 'imbecil', 'idiota',
    'estúpido', 'estupido', 'pendejo', 'pendeja', 'mamada', 'verga', 'chingar',
    'pinche', 'culero', 'ojete', 'marica', 'maricon', 'maricón',
    # Términos racistas y discriminatorios
    'negro de mierda', 'gitano', 'moro', 'sudaca', 'panchito', 'chino de mierda',
    'nazi', 'hitler', 'fascista', 'supremacista', 'racista',
    # Palabras en inglés
    'fuck', 'shit', 'bitch', 'asshole', 'damn', 'nigger', 'faggot', 'retard'
]

# Términos que indican contenido racista o discriminatorio
CONTENIDO_DISCRIMINATORIO = [
    'raza superior', 'raza inferior', 'supremacía', 'holocausto', 'genocide',
    'exterminar', 'eliminar raza', 'odio racial', 'discriminación racial',
    'todos los', 'muerte a', 'matar a todos'
]

# Funciones para operaciones DB en contexto async
@sync_to_async
def get_or_create_session(session_id, user):
    return ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={'user': user}
    )

@sync_to_async
def create_message(session, role, content):
    return Message.objects.create(
        session=session,
        role=role,
        content=content
    )

@sync_to_async
def get_chat_history(session_id):
    session = ChatSession.objects.filter(session_id=session_id).first()
    if not session:
        return []
    
    messages = Message.objects.filter(session=session).order_by('timestamp')[:10]
    return [
        {"role": msg.role, "content": msg.content} 
        for msg in messages
    ]

def moderar_contenido(mensaje):
    """
    Modera el contenido del mensaje para detectar palabras malsonantes,
    contenido racista o discriminatorio.
    """
    mensaje_lower = mensaje.lower()
    
    # Verificar palabras censuradas
    for palabra in PALABRAS_CENSURADAS:
        if palabra in mensaje_lower:
            return {
                'es_inapropiado': True,
                'tipo': 'lenguaje_inapropiado',
                'mensaje': 'Por favor, mantén un lenguaje respetuoso en nuestro chat. Estoy aquí para ayudarte con información sobre EV-EMAPs.'
            }
    
    # Verificar contenido discriminatorio
    for termino in CONTENIDO_DISCRIMINATORIO:
        if termino in mensaje_lower:
            return {
                'es_inapropiado': True,
                'tipo': 'contenido_discriminatorio',
                'mensaje': 'No tolero contenido discriminatorio, racista u ofensivo. Mi objetivo es proporcionar información útil sobre EV-EMAPs en un ambiente respetuoso.'
            }
    
    # Detectar patrones de odio usando expresiones regulares
    patrones_odio = [
        r'odio a (los|las) \w+',
        r'muerte a (los|las) \w+',
        r'eliminar a (los|las) \w+',
        r'todos los \w+ son \w+',
        r'las \w+ son todas \w+'
    ]
    
    for patron in patrones_odio:
        if re.search(patron, mensaje_lower):
            return {
                'es_inapropiado': True,
                'tipo': 'discurso_de_odio',
                'mensaje': 'No puedo responder a mensajes que contengan discurso de odio. Estoy aquí para ayudarte con información sobre nuestros servicios de carga de vehículos eléctricos.'
            }
    
    return {
        'es_inapropiado': False,
        'tipo': None,
        'mensaje': None
    }

# Funciones para obtener datos reales de la base de datos
@sync_to_async
def obtener_electrolineras_reales():
    """Obtiene datos reales de electrolineras desde la base de datos"""
    from electrolineras.models import PuntoRecarga, Conector
    try:
        puntos = PuntoRecarga.objects.select_related('tipo_conector').all()[:10]  # Limitar a 10 para no sobrecargar
        
        electrolineras = []
        for punto in puntos:
            # Obtener estado de forma segura
            estado = getattr(punto, 'estado', 'disponible')
            
            electrolinera = {
                'nombre': punto.nombre,
                'direccion': punto.direccion,
                'latitud': float(punto.latitud) if punto.latitud else None,
                'longitud': float(punto.longitud) if punto.longitud else None,
                'potencia_kw': punto.potencia_kw,
                'estado': estado,
                'conector': punto.tipo_conector.denominacion if punto.tipo_conector else 'No especificado',
                'energia_total': getattr(punto, 'energia_suministrada_total', 0)
            }
            electrolineras.append(electrolinera)
        
        return electrolineras
    except Exception as e:
        print(f"Error obteniendo electrolineras reales: {e}")
        return []

@sync_to_async
def obtener_conectores_reales():
    """Obtiene datos reales de conectores desde la base de datos"""
    from electrolineras.models import Conector
    try:
        conectores = Conector.objects.all()
        
        conectores_data = []
        for conector in conectores:
            conector_data = {
                'codigo': conector.codigo,
                'denominacion': conector.denominacion,
                'potencia_kw': conector.potencia_kw
            }
            conectores_data.append(conector_data)
        
        return conectores_data
    except Exception as e:
        print(f"Error obteniendo conectores reales: {e}")
        return []

@sync_to_async
def obtener_estadisticas_uso():
    """Obtiene estadísticas de uso real de la plataforma"""
    from electrolineras.models import PuntoRecarga
    from django.contrib.auth.models import User
    try:
        total_puntos = PuntoRecarga.objects.count()
        # Usar filter con try/catch por si no existe el campo estado
        try:
            puntos_disponibles = PuntoRecarga.objects.filter(estado='disponible').count()
        except:
            puntos_disponibles = total_puntos
        
        total_usuarios = User.objects.count()
        
        return {
            'total_puntos': total_puntos,
            'puntos_disponibles': puntos_disponibles,
            'total_usuarios': total_usuarios
        }
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {
            'total_puntos': 0,
            'puntos_disponibles': 0,
            'total_usuarios': 0
        }

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Cuando un usuario se conecta, le asignamos una sala única
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default')
        
        # Asignar ID de sesión basado en el usuario o crear uno nuevo para usuarios anónimos
        if self.scope['user'] and not isinstance(self.scope['user'], AnonymousUser):
            self.session_id = f"user_{self.scope['user'].id}"
            user = self.scope['user']
        else:
            self.session_id = f"anon_{str(uuid.uuid4())}"
            user = None
        
        # Crear o recuperar la sesión de chat
        session, created = await get_or_create_session(self.session_id, user)
        self.chat_session = session
        
        # Aceptar la conexión
        await self.accept()
          # Mensaje de bienvenida
        welcome_message = '¡Hola! Soy el asistente virtual de EV-EMAPs con IA habilitada. ¿En qué puedo ayudarte?' if OLLAMA_AVAILABLE else '¡Hola! Soy el asistente virtual de EV-EMAPs. ¿En qué puedo ayudarte?'
        
        await self.send(text_data=json.dumps({
            'type': 'welcome',
            'message': welcome_message
        }))

    async def disconnect(self, code):
        pass  # No necesitamos hacer nada especial al desconectar

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
            
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            # Moderar contenido antes de procesar
            moderacion = moderar_contenido(message)
            
            if moderacion['es_inapropiado']:
                # Enviar mensaje de moderación sin guardar el mensaje original
                await self.send(text_data=json.dumps({
                    'type': 'message',
                    'message': moderacion['mensaje'],
                    'role': 'system'
                }))
                
                # Guardar registro de moderación (opcional)
                await create_message(
                    session=self.chat_session,
                    role='system',
                    content=f"Mensaje moderado ({moderacion['tipo']}): {moderacion['mensaje']}"
                )
                return
            
            # Guardar mensaje del usuario solo si pasa la moderación
            await create_message(
                session=self.chat_session,
                role='user',
                content=message
            )
            
            # Envío de confirmación de recepción
            await self.send(text_data=json.dumps({
                'type': 'status',
                'message': 'Pensando...'            }))
            
            # Generar respuesta usando Ollama únicamente
            response = await self.get_ollama_response(message)
            
            # Guardar respuesta en BD
            await create_message(
                session=self.chat_session,
                role='assistant',
                content=response
            )
            
            # Enviar respuesta al usuario
            await self.send(text_data=json.dumps({
                'type': 'message',
                'message': response,
                'role': 'assistant'
            }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'message',
                'message': "No pude entender tu mensaje. Por favor, inténtalo de nuevo.",
                'role': 'assistant'
            }))
        except Exception as e:
            # Log del error específico para debugging (sin mostrarlo al usuario)
            print(f"Error en ChatConsumer: {type(e).__name__}: {str(e)}")              # Respuesta amigable al usuario
            await self.send(text_data=json.dumps({
                'type': 'message',
                'message': "Lo siento, he tenido un problema técnico temporal. ¿Podrías intentar hacer tu pregunta de nuevo? Si el problema persiste, puedes contactar con julio@juliomalaga.me.",
                'role': 'assistant'
            }))

    async def get_ollama_response(self, message):
        """Obtener respuesta de Ollama sin información de negocio, solo datos reales cuando sea necesario"""
        try:
            # Obtener datos reales de la base de datos solo cuando sea relevante
            electrolineras_reales = await obtener_electrolineras_reales()            # Construir contexto mínimo solo con datos específicos
            contexto_datos = ""
            palabras_busqueda = ['electrolinera', 'cargador', 'tesla', 'palma', 'palmilla', 'ubicacion', 'coordenadas', 'latitud', 'longitud', 'donde esta', 'conector', 'enchufe', 'tipo', 'ccs', 'chademo', 'schuko', 'punto de carga', 'estacion de carga', 'potencia', 'kw']
            
            es_pregunta_especifica = any(term in message.lower() for term in palabras_busqueda)
            
            if es_pregunta_especifica:
                if not electrolineras_reales:
                    return "No dispongo de datos específicos sobre electrolineras en la base de datos en este momento. Por favor, contacta con el administrador para obtener información actualizada."
                
                contexto_datos = "\nDatos específicos disponibles en la base de datos:\n"
                for electrolinera in electrolineras_reales:
                    contexto_datos += f"- Nombre: {electrolinera['nombre']}\n"
                    contexto_datos += f"  Dirección: {electrolinera['direccion']}\n"
                    if electrolinera['latitud'] and electrolinera['longitud']:
                        contexto_datos += f"  Coordenadas: Latitud {electrolinera['latitud']}, Longitud {electrolinera['longitud']}\n"
                    contexto_datos += f"  Potencia: {electrolinera['potencia_kw']} kW\n"
                    contexto_datos += f"  Tipo de conector: {electrolinera['conector']}\n"
                    contexto_datos += f"  Estado actual: {electrolinera['estado']}\n"
                    if electrolinera['energia_total'] > 0:
                        contexto_datos += f"  Energía total suministrada: {electrolinera['energia_total']} kWh\n"
                    contexto_datos += "\n"
            
            # Prompt específico que evita respuestas genéricas
            if contexto_datos:
                system_prompt = f"""Responde ÚNICAMENTE usando estos datos específicos de la base de datos. Si la información solicitada no está en estos datos exactos, responde claramente: "No dispongo de esa información específica en la base de datos":{contexto_datos}

REGLAS IMPORTANTES:
- Solo usa los datos proporcionados arriba
- No inventes información  
- No hagas generalizaciones
- Si no tienes el dato exacto solicitado, dilo claramente"""
            else:
                system_prompt = "Responde usando tu conocimiento general. Esta no parece ser una pregunta específica sobre datos de electrolineras de la aplicación."
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2:3b",
                        "prompt": f"Sistema: {system_prompt}\n\nUsuario: {message}\n\nAsistente:",
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "max_tokens": 400
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    respuesta = result.get('response', '').strip()
                    print(f"DEBUG - Pregunta: {message}")
                    print(f"DEBUG - Contexto: {contexto_datos[:100]}...")
                    print(f"DEBUG - Respuesta: {respuesta[:100]}...")
                    return respuesta
                else:
                    print(f"Error Ollama: {response.status_code}")
                    return "Lo siento, hay un problema técnico en este momento."
                    
        except Exception as e:
            print(f"Error en get_ollama_response: {type(e).__name__}: {str(e)}")
            return "Lo siento, he tenido un problema técnico. Intenta de nuevo."
