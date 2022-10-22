from django.contrib.auth.forms import UserCreationForm
# from .models import Profile
from django import forms
from users.models import User


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'location',
            'birth_date',
            'avatar',
            'background',
            'bio'
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'bio',
            'location',
            'birth_date',
            'avatar',
            'background'
        )
