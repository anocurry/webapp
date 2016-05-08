from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'email'}))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'username or email'}))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'placeholder': 'password'}))

class ResetForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'username or email'}))

class NewPasswordForm(forms.Form):
    new_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
