from django.conf.urls import url

from . import views

app_name='user'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^newpostform/$', views.newpostform, name='newpostform'),
    url(r'^(?P<post_id>[0-9]+)/newpostform/$', views.newpostformid, name='newpostformid'),
    url(r'^newpost/$', views.newpost, name='newpost'),
    url(r'^sitenamefind/$', views.sitenamefind, name='sitenamefind'),
    url(r'^sitenamelist/$', views.sitenamelist, name='sitenamelist'),
    url(r'^deletepost/$', views.deletepost, name='deletepost'),
    url(r'^(?P<user_id>[0-9]+)/$', views.search, name='search'),
    url(r'^search/$', views.searchuser, name='searchuser'),
    url(r'^viewaspublic/$', views.viewaspublic, name='viewaspublic'),
    url(r'^viewasconnected/$', views.viewasconnected, name='viewasconnected'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^customize/$', views.customize, name='customize'),
    url(r'^editsettings/$', views.editsettings, name='editsettings'),
    url(r'^editprofileimg/$', views.editprofileimg, name='editprofileimg'),
    url(r'^editbgimg/$', views.editbgimg, name='editbgimg'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^readnotifs/$', views.readnotifs, name='readnotifs'),
    url(r'^(?P<user_id>[0-9]+)/newnotif/$', views.newnotif, name='newnotif'),
    url(r'^(?P<user_id>[0-9]+)/cancelnotif/$', views.cancelnotif, name='cancelnotif'),
    url(r'^connections/$', views.connections, name='connections'),
    url(r'^(?P<user_id>[0-9]+)/newconnect/$', views.newconnect, name='newconnect'),
    url(r'^(?P<user_id>[0-9]+)/disconnect/$', views.disconnect, name='disconnect'),
    url(r'^custom/$', views.custom, name='custom'),
    url(r'^customsubmit/$', views.customsubmit, name='customsubmit'),
    url(r'^logout/$', views.logout, name='logout'),
]
