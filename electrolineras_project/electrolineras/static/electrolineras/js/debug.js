// Script de depuración para la funcionalidad de carga
console.log('Script de depuración cargado');

// Función para probar la API de iniciar carga directamente
async function probarIniciarCarga(reservaId) {
    try {
        console.log(`Intentando iniciar carga para reserva ID: ${reservaId}`);
        
        // Obtener token CSRF
        const csrftoken = getCookie('csrftoken');
        console.log('CSRF Token:', csrftoken);
        
        const response = await fetch('/electrolineras/api/iniciar-carga/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ reserva_id: reservaId })
        });
        
        console.log('Respuesta de la API:', response.status);
        const data = await response.json();
        console.log('Datos de la respuesta:', data);
        
        return data;
    } catch (error) {
        console.error('Error al iniciar carga:', error);
        return null;
    }
}

// Función para obtener token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Exponer funciones para uso desde la consola
window.debugApi = {
    probarIniciarCarga,
    getCookie
};

console.log('Puedes probar la API ejecutando: window.debugApi.probarIniciarCarga(14)');
