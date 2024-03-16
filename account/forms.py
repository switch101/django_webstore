from django.contrib.auth.forms import UserCreationForm
from django import forms

from account.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'password1', 'password2', 'name', 'surname', 'profile_picture', 'address', 'city', 'zip_code',
            'email', 'phone_number')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'surname', 'profile_picture', 'address', 'city', 'zip_code', 'email',
                  'phone_number']
