from django.conf.urls import url

from . import views

app_name='main'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^newuser/$', views.newuser, name='newuser'),
    url(r'^login/$', views.login, name='login'),
    url(r'^loginauth/$', views.loginauth, name='loginauth'),
]
