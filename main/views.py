from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse
from django.db.models import Q

from user.models import User


# Create your views here.
def index(request):
    template = loader.get_template('main/index.html')
    return HttpResponse(template.render({}, request))

def register(request):
    template = loader.get_template('main/register.html')
    return HttpResponse(template.render({}, request))

def newuser(request):
    try:
        #check if there's a user with same username or email
        u = User.objects.get(Q(username=request.POST['username']) | Q(email=request.POST['email']))
    except (User.DoesNotExist): #if there is not... create a new user
        newuser = User(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'], displayname=request.POST['username'], description="default description", vis=1, profileImg="testimg", bgImg="testBg", useBg=False)
        newuser.save()
        return HttpResponseRedirect(reverse('main:login')) #... and redirect to login page
    #otherwise, redirect back to registration page with an error message
    return render(request, 'main/register.html', {
        'error_message': "The username or email has already been used. Would you like to login?",
    })

def login(request):
    template = loader.get_template('main/login.html')
    return HttpResponse(template.render({}, request))

def loginauth(request):
    try:
        #check if there's a user with same username or email
        u = User.objects.get(Q(username=request.POST['username']) | Q(email=request.POST['username']))
    except (User.DoesNotExist): #if there is not... redirect to the login page
        return render(request, 'main/login.html', {
            'error_message': "This username or email does not exist. Did you enter it correctly?",
        })

    #if user exists, check if the password match...
    if (u.password != request.POST['password']):
        return render(request, 'main/login.html', {
            'error_message': "The password was incorrect. Please try again.",
        })
    #otherwise, return the profile page with login details
    request.session['login_id'] = u.id
    request.session['loggedin'] = True
    template = loader.get_template('user/index.html')
    return HttpResponseRedirect(reverse('user:index'))
