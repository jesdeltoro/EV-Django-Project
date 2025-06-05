from django.core.mail import send_mail
from django.conf import settings

# Prueba envío de correo
def test_email():
    subject = 'Prueba de envío de correo'
    message = 'Este es un mensaje de prueba desde Django. Si lo ves, la configuración de correo está funcionando correctamente.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['jjse79@hotmail.com']  # Reemplaza con tu correo donde quieres recibir la prueba
    
    result = send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
    
    if result:
        print("Correo enviado correctamente")
    else:
        print("Error al enviar el correo")

# Ejecutar la función cuando se importe el script
test_email()
