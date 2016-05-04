from django import forms
from django.forms import ModelForm

from .models import User, Post

class PostForm_2(forms.Form):
    postid = forms.CharField(max_length=100)
    sitename = forms.CharField(max_length=50)
    siteusername = forms.CharField(max_length=50)
    email = forms.EmailField()
    url = forms.URLField()
    usage = forms.CharField(max_length=50)
    category = forms.CharField(max_length=50)
    description = forms.CharField(max_length=100)
    vis = forms.CharField(max_length=50)
    logo = forms.CharField(max_length=200)

class PostForm(forms.Form):
    class Meta:
        model = Post
        fields = ['post_id', 'sitename', 'siteusername', 'email', 'url', 'usage', 'category', 'description', 'vis', 'logo']

class AccountForm_2(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'value': 'your username'}))
    password = forms.CharField(max_length=50)
    email = forms.EmailField()
    displayname = forms.CharField(max_length=50)
    description = forms.CharField(max_length=200)
    vis = forms.CharField(max_length=50)
    profileImg = forms.ImageField() #change to imagefield?
    bgImg = forms.CharField(max_length=200)   #change to imagefield?
    useBg = forms.CharField(max_length=50)

class AccountForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'displayname', 'description', 'vis', 'profileImg', 'bgImg', 'useBg']
