from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse
from django.db.models import Q
import datetime

from django.core.files import File
import os

from .models import User, Post, Connection, Notification
from .forms import PostForm, AccountForm


# Create your views here.
def index(request):
    #display the logged in user here
    u = getLoggedInUser(request)
    if u is None:
        #redirect to the main page if the user is not logged in
        #template = loader.get_template('main/index.html')
        #return HttpResponse(template.render({}, request))
        return HttpResponseRedirect(reverse('main:index'))
    form = PostForm()
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/index.html')
    return HttpResponse(template.render({'user': u, 'form': form, 'notifNum': notifNum, 'ownprofile': True}, request))

def newpostform(request):
    form = PostForm()
    template = loader.get_template('user/postform.html')
    return HttpResponse(template.render({'form': form,}, request))

def newpostformid(request, post_id):
    p = Post.objects.get(id=post_id)
    form = PostForm(instance=p)
    template = loader.get_template('user/postform.html')
    return HttpResponse(template.render({'form': form,}, request))

def getLoggedInUser(request):
    uid = request.session.get('login_id')
    try:
        u = User.objects.get(id=uid)
    except User.DoesNotExist:
        return None
    return u

def search(request, user_id):
    try:
        searcheduser = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    template = loader.get_template('user/search.html')

    u = getLoggedInUser(request)
    notifNum = getUnreadNotifNum(request)
    form = PostForm()
    ownprofile = False
    if (int(user_id) == request.session.get('login_id')): #or use int(user_id)
        ownprofile = True
    c = isConnected(request, user_id)
    n = 0
    if c is None:
        connected = False
        #do something to find notif...
        n = findNotif(request, user_id)
    else:
        connected = True
    return HttpResponse(template.render({'user': u, 'notifNum': notifNum, 'searcheduser': searcheduser, 'ownprofile': ownprofile, 'form': form, 'connected': connected, 'notif': n,}, request))

def searchuser(request):
    if request.POST['user_name']:
        searcheduser = User.objects.get(username=request.POST['user_name'])
        return search(request, searcheduser.id)

def settings(request):
    uid = request.session.get('login_id')
    u = User.objects.get(id=uid)
    notifNum = getUnreadNotifNum(request)
    form = AccountForm(instance=u)
    template = loader.get_template('user/settings.html')
    return HttpResponse(template.render({'form': form, 'user': u, 'notifNum': notifNum}, request))

def customize(request):
    uid = request.session.get('login_id')
    u = User.objects.get(id=uid)
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/customize.html')
    return HttpResponse(template.render({'user': u, 'notifNum': notifNum}, request))

def editsettings(request):
    #do checking for password first...
    u = getLoggedInUser(request)
    form = AccountForm(instance=u)
    if (u.password != request.POST['password']):
        return render(request, 'user/settings.html', {
            'error_message': "Your password was incorrect. Please try again.",
            'form': form,
            'user': u,
        })
    try:
        u1 = User.objects.get(~Q(id=u.id) & Q(username=u.username) | ~Q(id=u.id) & Q(email=u.email))
    except User.DoesNotExist:
        #if details do not clash, save the user's new settings...
        form = AccountForm(request.POST, request.FILES)
        if form.is_valid():
            if (~bool(request.FILES)):
                pimg = u.profileImg
                #bgimg = u.bgImg
            else:
                pimg = request.FILES['profileImg']
                #bgImg = request.FILES['bgImg']
            u.username = request.POST['username']
            u.password = request.POST['password']
            u.email = request.POST['email']
            u.displayname = request.POST['displayname']
            u.description = request.POST['description']
            u.vis = request.POST['vis']
            u.profileImg = pimg
            #u.bgImg = bgimg
            u.save()
            return HttpResponseRedirect(reverse('user:settings'))
        else:
            form = AccountForm(instance=u)
            return render(request, 'user/settings.html', {
                'error_message': "Some error occurred in editing. Please try again.",
                'form': form,
                'user': u,
            })

    #otherwise, return with an error message
    return render(request, 'user/settings.html', {
        'error_message': "The username or email is already in use. Please try again.",
        'form': form,
    })

def editprofileimg(request):
    u = getLoggedInUser(request)
    if (bool(request.FILES)):
        pimg = request.FILES['profileImg']
        u.profileImg = pimg
        u.save()
        return HttpResponseRedirect(reverse('user:customize'))
    #if failed, return to user's customize page
    return render(request, 'user/customize.html', {
        'error_message': "Something went wrong. Please try again.",
    })

def editbgimg(request):
    u = getLoggedInUser(request)
    if (bool(request.FILES)):
        bgimg = request.FILES['bgImg']
        u.bgImg = bgimg
        u.save()
        return HttpResponseRedirect(reverse('user:customize'))
    #if failed, return to user's customize page
    return render(request, 'user/customize.html', {
        'error_message': "Something went wrong. Please try again.",
    })


def notifications(request):
    u = getLoggedInUser(request)
    notifs = Notification.objects.filter(Q(fromuser=u.id) & Q(is_accepted=True) | Q(touser=u.id))
    toread = Notification.objects.filter(Q(fromuser=u.id) & Q(is_accepted=True) | Q(touser=u.id) & Q(is_accepted=False))
    for n in toread:
        n.is_read = True
        n.save()
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/notifications.html')
    return HttpResponse(template.render({'user': u, 'notifs': notifs, 'notifNum': notifNum}, request))

def getUnreadNotifNum(request):
    u = getLoggedInUser(request)
    if u:
        num = Notification.objects.filter(Q(fromuser=u.id) & Q(is_accepted=True) & Q(is_read=False) |  Q(touser=u.id) & Q(is_accepted=False) & Q(is_read=False)).count()
        return num

def newpost(request):
    u = getLoggedInUser(request)
    if (request.POST['postid'] != ''): #check if the user is editing an existing post
        try:
            p = Post.objects.get(id=request.POST['postid'])
        except Post.DoesNotExist:
            return render(request, 'user/index.html', {
                'error_message': "This post no longer exists.",
            })
        #get all the form data and edit the post
        form = PostForm(request.POST, request.FILES)
        path = 'logo/default/' + 'tumblr.png'
        print(os.path.exists('media/' + path))
        if form.is_valid():
            p.sitename = request.POST['sitename']
            p.siteusername = request.POST['siteusername']
            p.email = request.POST['email']
            p.url = request.POST['url']
            p.usage = request.POST['usage']
            p.category = request.POST['category']
            p.description = request.POST['description']
            p.vis = request.POST['vis']
            if (bool(request.FILES)):
                p.logo = request.FILES['logo']
            p.save()
            return HttpResponseRedirect(reverse('user:index'))
        else:
            return render(request, 'user/index.html', {
                'error_message': "Something went wrong with editing. Please try again.",
                'form': form,
                'ownprofile': True,
            })
    else: #if not, create a new post and add it
        if bool(request.FILES): #if the user has uploaded a logo
            l = request.FILES['logo']
        else:
            path = 'logo/default/' + request.POST['sitename'] + '.png'
            if (os.path.exists('media/' + path)): #check if there's a default logo
                l = path
            else:
                l = 'logo/default/pizza.png'
        print(l)
        p = u.post_set.create(sitename=request.POST['sitename'], siteusername=request.POST['siteusername'], email=request.POST['email'], url=request.POST['url'], usage=request.POST['usage'], category=request.POST['category'], description=request.POST['description'], vis=request.POST['vis'], logo=l)
        return HttpResponseRedirect(reverse('user:index'))

def newnotif(request, user_id):
    uid = request.session.get('login_id')
    n=Notification(fromuser=uid, touser=user_id, message='test')
    n.save()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))


def cancelnotif(request, user_id):
    uid = request.session.get('login_id')
    try:
        n=Notification.objects.filter(fromuser=uid, touser=user_id, is_accepted=False).latest('notif_date')
    except Notification.DoesNotExist:
        return HttpResponseRedirect(reverse('user:search', args=(user_id,)))
    n.delete()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))

def newconnect(request, user_id):
    uid = request.session.get('login_id')
    c = isConnected(request, user_id)
    if c is None:
        c=Connection(fromuser=uid, touser=user_id)
        c.save()
        try:
            n=Notification.objects.filter(fromuser=user_id, touser=uid, message='test').latest('notif_date')
        except Notification.DoesNotExist:
            return HttpResponseRedirect(reverse('user:search', args=(user_id,)))
        n.is_accepted = True
        n.is_read = False
        n.notif_date = datetime.datetime.now()
        n.save()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))


def disconnect(request, user_id):
    uid = request.session.get('login_id')
    c = isConnected(request, user_id)
    if c is None:
        #do nothing
        return HttpResponseRedirect(reverse('user:search', args=(user_id,)))
    c.delete()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))


def isConnected(request, user_id):
    uid = request.session.get('login_id')
    try:
        c = Connection.objects.get((Q(fromuser=uid) & Q(touser=user_id)) | (Q(fromuser=user_id) & Q(touser=uid))) #find if they have established a connection
    except Connection.DoesNotExist:
        return None
    return c

def findNotif(request, user_id):
    uid = request.session.get('login_id')
    try:
        n = Notification.objects.get(fromuser=uid, touser=user_id, message='test', is_accepted=False)
        #display as 'request sent'
        return 1
    except Notification.DoesNotExist:
        try:
            n = Notification.objects.get(fromuser=user_id, touser=uid, message='test', is_accepted=False)
            #display as 'respond to request'
            return 2
        except Notification.DoesNotExist:
            #display as 'send connection' or something
            return 0

def logout(request):
    try:
        del request.session['login_id']
        del request.session['loggedin']
        #do something else
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('main:index'))
