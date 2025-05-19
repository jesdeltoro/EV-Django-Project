from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserCreationFormWithEmail(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. 254 carácteres como máximo y debe ser válido.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El email ya está registrado, prueba con otro.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'link', 'alias']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class':'form-control-file mt-3'}),
            'bio': forms.Textarea(attrs={'class':'form-control mt-3', 'rows':3, 'placeholder':'Biografía'}),
            'link': forms.URLInput(attrs={'class':'form-control mt-3', 'placeholder':'Enlace'}),
            'alias': forms.TextInput(attrs={'class':'form-control mt-3', 'placeholder':'Alias'}),
        }

    def clean_alias(self):
        alias = self.cleaned_data.get("alias")
        if alias:
            # Get current instance
            instance = getattr(self, 'instance', None)
            # Check for duplicates excluding current instance
            queryset = Profile.objects.filter(alias=alias)
            if instance and instance.pk:
                queryset = queryset.exclude(pk=instance.pk)
            if queryset.exists():
                raise forms.ValidationError("El alias ya está registrado, prueba con otro.")
        return alias


class EmailForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Requerido. 254 carácteres como máximo y debe ser válido.")

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if 'email' in self.changed_data:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("El email ya está registrado, prueba con otro.")
        return email


class AliasForm(forms.ModelForm):
    alias = forms.CharField(required=False, help_text="Opcional. Introduce un alias único para identificarte.")

    class Meta:
        model = Profile
        fields = ['alias']

    def clean_alias(self):
        alias = self.cleaned_data.get("alias")
        if alias:
            # Get current instance
            instance = getattr(self, 'instance', None)
            # Check for duplicates excluding current instance
            queryset = Profile.objects.filter(alias=alias)
            if instance and instance.pk:
                queryset = queryset.exclude(pk=instance.pk)
            if queryset.exists():
                raise forms.ValidationError("El alias ya está registrado, prueba con otro.")
        return alias