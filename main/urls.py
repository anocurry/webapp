from django.conf.urls import url

from . import views

app_name='main'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^newuser/$', views.newuser, name='newuser'),
    url(r'^login/$', views.login, name='login'),
    url(r'^loginauth/$', views.loginauth, name='loginauth'),
    url(r'^reset/$', views.reset, name='reset'),
    url(r'^resetpassword/$', views.resetpassword, name='resetpassword'),
    url(r'^(?P<user_id>[0-9]+)/resetauth/$', views.resetauth, name='resetauth'),
    url(r'^(?P<user_id>[0-9]+)/resetauthprocess/$', views.resetauthprocess, name='resetauthprocess'),
]
