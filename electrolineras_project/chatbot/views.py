from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
import json
import uuid

def chat_room(request, room_name=None):
    # Si no se proporciona un nombre de sala, generamos uno aleatorio
    if not room_name:
        room_name = str(uuid.uuid4())[:8]
    
    return render(request, 'chatbot/chat_room.html', {
        'room_name': mark_safe(json.dumps(room_name)),
    })
