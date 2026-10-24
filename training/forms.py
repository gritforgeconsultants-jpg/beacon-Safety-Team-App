from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegistrationForm(UserCreationForm):
    position = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "position", "password1", "password2")
