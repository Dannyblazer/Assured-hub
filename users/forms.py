from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from users.models import Account, Server

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60)
    required_css_class = 'bold'

    class Meta:
        model = Account
        fields = {"email", "username", "password1", "password2"}
    
    field_order = ['email', 'username',]

    

class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid login")

class AccountUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = ('email', 'username')
    
    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
            except Account.DoesNotExist:
                return email
            raise forms.ValidationError("Email {} is already in use.".format(email))
    
    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
            except Account.DoesNotExist:
                return username
            raise forms.ValidationError("Username {} is already in use.".format(username))
    
class ServerRegistrationForm(forms.ModelForm):

    class Meta:
        model = Server
        fields = {'ip', 'port'}
