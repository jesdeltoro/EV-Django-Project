from .forms import UserCreationFormWithEmail, ProfileForm, EmailForm
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django import forms
from .models import Profile
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from typing import cast
from django.shortcuts import render, redirect
from .verification import activate_account

# Create your views here.
class SignUpView(CreateView):
    form_class = UserCreationFormWithEmail
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login') + '?verification_sent'

    def form_valid(self, form):
        # Guardar el usuario pero marcarlo como inactivo hasta que verifique su correo
        user = form.save(commit=False)
        user.is_active = False  # El usuario estará inactivo hasta verificar email
        user.save()
        
        # Importar las utilidades para la verificación
        from django.contrib.sites.shortcuts import get_current_site
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from .verification import account_activation_token
        
        # Construir el correo de verificación
        current_site = get_current_site(self.request)
        mail_subject = 'Activa tu cuenta en el Sistema de Electrolineras'
        
        message = f"""¡Hola {user.username}!

Por favor, haz clic en el siguiente enlace para confirmar y activar tu cuenta:

http://{current_site.domain}/accounts/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{account_activation_token.make_token(user)}/

Si tú no solicitaste este registro, puedes ignorar este correo.

¡Gracias por unirte a nosotros!

Equipo del Sistema de Electrolineras
"""
        
        try:
            send_mail(
                subject=mail_subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Si hay algún error con el email, no afectar el registro
            print(f"Error enviando email de verificación: {e}")
            
        # Devolver la respuesta normal de CreateView
        return super().form_valid(form)
        
    def get_form(self, form_class=None):
        form = super(SignUpView, self).get_form()
        # Modificar en tiempo real
        form.fields["username"].widget = forms.TextInput(
            attrs={"class":"form-control mb-2", "placeholder":"Nombre de usuario"})
        form.fields["email"].widget = forms.EmailInput(
            attrs={"class":"form-control mb-2", "placeholder":"Dirección email"})
        form.fields["password1"].widget = forms.PasswordInput(
            attrs={"class":"form-control mb-2", "placeholder":"Contraseña"})
        form.fields["password2"].widget = forms.PasswordInput(
            attrs={"class":"form-control mb-2", "placeholder":"Repite la contraseña"})
        
        # Personalizar las etiquetas de los campos de contraseña
        form.fields["password1"].label = "Contraseña"
        form.fields["password2"].label = "Contraseña (confirmación)"
        return form

def activate(request, uidb64, token):
    # Activar la cuenta del usuario
    if activate_account(uidb64, token):
        return redirect(reverse_lazy("login") + "?activated")
    else:
        return render(request, "registration/activation_failed.html")


@method_decorator(login_required, name="dispatch")
class ProfileUpdate(UpdateView):
    form_class = ProfileForm
    success_url = reverse_lazy("profile")
    template_name = "registration/profile_form.html"

    def get_object(self, queryset=None):
        # recuperar el objeto que se va editar
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

@method_decorator(login_required, name="dispatch")
class EmailUpdate(UpdateView):
    form_class = EmailForm
    success_url = reverse_lazy("profile")
    template_name = "registration/profile_email_form.html"

    def get_object(self, queryset=None) -> User:
        # recuperar el objeto que se va editar
        return cast(User, self.request.user)

    def get_form(self, form_class=None):
        form = super(EmailUpdate, self).get_form()
        # Modificar en tiempo real
        form.fields["email"].widget = forms.EmailInput(
            attrs={"class":"form-control mb-2", "placeholder":"Email"})
        return form
