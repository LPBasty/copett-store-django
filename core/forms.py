from django import forms
from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        # Aquí le inyectamos tu diseño oscuro y dorado directo desde Python
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Tus apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'correo@ejemplo.com'}),
        }
