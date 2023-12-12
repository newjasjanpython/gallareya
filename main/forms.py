from django import forms
from artist.models import MeUser
from .models import WebUser, Artist
from django.contrib.auth import login


class MultiModelCreationForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Foydalanuvchi nomi', 'class': 'open-is-valid', 'data-next-selector': '#super_is_email', 'required': 'true'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Elektron pochta', 'class': 'open-is-valid', 'data-next-selector': '#super_is_password', 'required': 'true'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Ism', 'class': 'open-is-valid', 'data-next-selector': '#super_is_last_name', 'required': 'true'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Parol', 'class': 'open-is-valid', 'data-next-selector': '#super_is_confirm-password', 'required': 'true'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Parolni tasdiqlang', 'class': 'open-is-valid', 'data-next-selector': '#super_is_image,#super_is_send', 'required': 'true'}))

    def is_valid(self) -> bool:
        data = super().is_valid()

        if self.cleaned_data.get('password1', 'rgbbbbbbbbr1') == self.cleaned_data.get('password2', '321udsf9871ui'):
            filtered = MeUser.objects.filter(username=self.cleaned_data['username'])
            if filtered:
                self.add_error("username", "Foydalanuvchi ro'yhatdan o'tib o'lgan")
                return False
        else:
            self.add_error("password1", "Parollar bir xil bo'lishi lozim")
        return data

    def save(self, commit=True):
        user = MeUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            privacy=self.cleaned_data.get('privacy', False)
        )

        return user
