from django.conf.urls import url

from . import views

app_name='user'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^newpost/$', views.newpost, name='newpost'),
    url(r'^(?P<user_id>[0-9]+)/$', views.search, name='search'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^editsettings/$', views.editsettings, name='editsettings'),
    url(r'^(?P<user_id>[0-9]+)/newnotif/$', views.newnotif, name='newnotif'),
    url(r'^(?P<user_id>[0-9]+)/cancelnotif/$', views.cancelnotif, name='cancelnotif'),
    url(r'^(?P<user_id>[0-9]+)/newconnect/$', views.newconnect, name='newconnect'),
    url(r'^(?P<user_id>[0-9]+)/disconnect/$', views.disconnect, name='disconnect'),
    url(r'^logout/$', views.logout, name='logout'),
]
