from django import forms
from django.core import exceptions
from veloce import validators
from veloce import models
from veloce.forms import utils
from datetime import date


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=50,
        validators=[validators.PasswordValidator]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=50,
        validators=[validators.PasswordValidator]
    )

    class Meta:
        model = models.VeloceUser
        exclude = [
            'user', 'created_at', 'updated_at'
        ]
        widgets = {
            'birthdate': forms.SelectDateWidget(
                years=range(1920, date.today().year - 17),
                empty_label=''
            ),
        }
        fields = ['first_name', 'last_name', 'email_address', 'password', 'confirm_password', 'user_role', 'gender',
                  'birthdate']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        utils.select_option(self)

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise exceptions.ValidationError('Passwords don\'t match.')


class LoginForm(forms.Form):
    full = ['username', 'password']

    username = forms.EmailField(
        widget=forms.EmailInput,
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        max_length=50
    )


class ChangePasswordForm(forms.Form):
    full = ['new_password', 'confirm_password', 'current_password']

    current_password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=50,
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=50,
        validators=[validators.PasswordValidator]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=50,
        validators=[validators.PasswordValidator]
    )

    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise exceptions.ValidationError('Your password and confirmation password do not match!')


class AuthProfileForm(forms.ModelForm):
    email_address = forms.CharField(max_length=254, required=True,
                                    widget=forms.EmailInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = models.VeloceUser
        exclude = [
            'user', 'user_role', 'created_at', 'updated_at'
        ]
        widgets = {
            'birthdate': forms.SelectDateWidget(
                years=range(1920, date.today().year - 17),
                empty_label=''
            ),
        }