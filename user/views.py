from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse
from django.db.models import Q

from .models import User, Post, Connection, Notification
from .forms import PostForm, AccountForm


# Create your views here.
def index(request):
    #display the logged in user here
    uid = request.session.get('login_id')
    u = User.objects.get(id=uid)
    form = PostForm(u)
    template = loader.get_template('user/index.html')
    return HttpResponse(template.render({'user': u, 'form': form,}, request))

def search(request, user_id):
    try:
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    template = loader.get_template('user/search.html')
    ownprofile = False
    if (u.id==request.session.get('login_id')): #or use int(user_id)
        ownprofile = True

    c = isConnected(request, user_id)
    n = 0
    if c is None:
        connected = False
        #do something to find notif...
        n = findNotif(request, user_id)
    else:
        connected = True
    return HttpResponse(template.render({'user': u, 'ownprofile': ownprofile, 'connected': connected, 'notif': n,}, request))

def settings(request):
    uid = request.session.get('login_id')
    u = User.objects.get(id=uid)
    form = AccountForm(instance=u)
    template = loader.get_template('user/settings.html')
    return HttpResponse(template.render({'form': form, 'user': u}, request))

def editsettings(request):
    #do checking for password first...
    uid = request.session.get('login_id')
    u = User.objects.get(id=uid)
    form = AccountForm(instance=u)
    if (u.password != request.POST['password']):
        return render(request, 'user/settings.html', {
            'error_message': "Your password was incorrect. Please try again.",
            'form': form,
        })
    try:
        u1 = User.objects.get(~Q(id=uid) & Q(username=u.username) | ~Q(id=uid) & Q(email=u.email))
    except User.DoesNotExist:
        #if details do not clash, save the user's new settings...
        form = AccountForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            u.username = request.POST['username']
            u.password = request.POST['password']
            u.email = request.POST['email']
            u.displayname = request.POST['displayname']
            u.description = request.POST['description']
            u.vis = request.POST['vis']
            u.profileImg = request.FILES['profileImg']
            u.bgImg = request.POST['bgImg']
            u.useBg = request.POST['useBg']
            u.save()
            return HttpResponseRedirect(reverse('user:settings'))
        else:
            return render(request, 'user/settings.html', {
                'error_message': "Some error occurred in editing. Please try again.",
                'form': form,
            })

    #otherwise, return with an error message
    return render(request, 'user/settings.html', {
        'error_message': "The username or email is already in use. Please try again.",
        'form': form,
    })


def newpost(request):
    uid = request.session.get('login_id')
    u = User.objects.get(id=uid)
    if (request.POST['postid'] != ''): #check if the user is editing an existing post
        try:
            p = Post.objects.get(id=request.POST['postid'])
        except Post.DoesNotExist:
            return render(request, 'user/index.html', {
                'error_message': "This post no longer exists.",
            })
        #get all the form data and edit the post
        p.sitename = request.POST['sitename']
        p.siteusername = request.POST['siteusername']
        p.email = request.POST['email']
        p.url = request.POST['url']
        p.usage = request.POST['usage']
        p.category = request.POST['category']
        p.description = request.POST['description']
        p.vis = request.POST['vis']
        p.logo = request.POST['logo']
        p.save()
        return HttpResponseRedirect(reverse('user:index'))
    else: #if not, create a new post and add it
        p = u.post_set.create(sitename=request.POST['sitename'], siteusername=request.POST['siteusername'], email=request.POST['email'], url=request.POST['url'], usage=request.POST['usage'], category=request.POST['category'], description=request.POST['description'], vis=request.POST['vis'], logo=request.POST['logo'])
        return HttpResponseRedirect(reverse('user:index'))

def newnotif(request, user_id):
    uid = request.session.get('login_id')
    n=Notification(fromuser=uid, touser=user_id, message='test')
    n.save()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))


def cancelnotif(request, user_id):
    uid = request.session.get('login_id')
    try:
        n=Notification.objects.get(fromuser=uid, touser=user_id, is_accepted=False)
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
            n=Notification.objects.get(fromuser=user_id, touser=uid, message='test')
        except Notification.DoesNotExist:
            return HttpResponseRedirect(reverse('user:search', args=(user_id,)))
        n.is_accepted = True
        n.is_read = False
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
