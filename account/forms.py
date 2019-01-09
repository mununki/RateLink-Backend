from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import MyUser, MyUserProfile, RateReader, MessageBox

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=254)

    class Meta:
        model = MyUser
        fields = ('email', 'nickname', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    email = forms.CharField(max_length=30)
    password = forms.CharField()

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = MyUserProfile
        fields = (
            'profile_name',
            'job_boolean',
            'company',
            'image',
        )

class RateReaderForm(forms.ModelForm):

    class Meta:
        model = RateReader
        fields = (
            'shower',
            'reader',
        )

class MessageSend(forms.ModelForm):

    class Meta:
        model = MessageBox
        fields = (
            'msg',
        )
