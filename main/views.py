from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from user.models import User
import user

from .forms import RegisterForm, LoginForm, ResetForm, NewPasswordForm

# Create your views here.

"""
    --- index(request) ---
    Returns a HttpResponse to display the main page.
"""
def index(request):
    template = loader.get_template('main/index.html')
    form = RegisterForm()
    try:
        u = user.views.getLoggedInUser(request)
    except User.DoesNotExist:
        return HttpResponse(template.render({}, request))
    notifNum = user.views.getUnreadNotifNum(request)
    return HttpResponse(template.render({'user': u, 'notifNum': notifNum, 'form': form}, request))

"""
    --- register(request) ---
    Returns a HttpResponse to display the registration page.
"""
def register(request):
    form = RegisterForm()
    try:
        u = User.objects.get(id=request.session['login_id'])
    except (KeyError, User.DoesNotExist):
        template = loader.get_template('main/register.html')
        return HttpResponse(template.render({'form': form}, request))
    #redirect if user is logged in
    return HttpResponseRedirect(reverse('user:index'))

"""
    --- newuser(request) ---
    Handles the request to create a new user.
    Redirects to the login page if a user is successfully created. The session variable 'register_success' is set to true.
    Otherwise, returns a HttpResponse to direct the user to registration page.
"""
def newuser(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        try:
            #check if there's a user with same username or email
            u = User.objects.get(Q(username__iexact=request.POST['username']) | Q(email=request.POST['email']))
        except (User.DoesNotExist): #if there is not... create a new user
            newuser = User(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'], displayname=request.POST['username'], description="default description", vis=1, profileImg="pic/default.png", bgImg="bg/default.jpg", useBg=False)
            newuser.save()
            request.session['register_success'] = True
            return HttpResponseRedirect(reverse('main:login')) #... and redirect to login page
        #otherwise, redirect back to registration page with an error message
        return render(request, 'main/register.html', {
            'error_message': "The username or email is already in use. Please try again.",
            'form': form,
        })
    else:
        return render(request, 'main/register.html', {
            'error_message': "Please fill up the form.",
            'form': form,
        })


"""
    --- login(request) ---
    Returns a HttpResponse to display the login page.
"""
def login(request):
    form = LoginForm()
    message = user.views.getMessage(request, 'register_success', "Your new account has been successfully created.")
    try:
        u = User.objects.get(id=request.session['login_id'])
    except (KeyError, User.DoesNotExist):
        u = None
    template = loader.get_template('main/login.html')
    return HttpResponse(template.render({'user': u, 'form': form, 'message': message}, request))

"""
    --- loginauth(request) ---
    Handles the request to login. The input is compared against the usernames and emails in the database.
    Redirects to user:index page if login is successful.
    Otherwise, returns a HttpResponse to direct the user back to the login page.
"""
def loginauth(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        try:
            #check if there's a user with same username or email
            u = User.objects.get(Q(username__iexact=request.POST['username']) | Q(email=request.POST['username']))
        except (User.DoesNotExist): #if there is not... redirect to the login page
            return render(request, 'main/login.html', {
                'error_message': "This username or email does not exist. Did you enter it correctly?",
                'form': form,
            })

        #if user exists, check if the password match...
        if (u.password != request.POST['password']):
            return render(request, 'main/login.html', {
                'error_message': "The password was incorrect. Please try again.",
                'form': form,
            })
        #otherwise, return the profile page with login details
        request.session['login_id'] = u.id
        request.session['loggedin'] = True
        return HttpResponseRedirect(reverse('user:index'))
    else:
        return render(request, 'main/login.html', {
            'error_message': "Please fill up the form.",
            'form': form,
        })

"""
    --- reset(request) ---
    Returns a HttpResponse to display the reset password page.
"""
def reset(request):
    form = ResetForm()
    try:
        u = User.objects.get(id=request.session['login_id'])
    except (KeyError, User.DoesNotExist):
        u = None
        template = loader.get_template('main/resetpassword.html')
        return HttpResponse(template.render({'user': u, 'form': form,}, request))
    #redirect if user is logged in
    return HttpResponseRedirect(reverse('main:login'))


"""
    --- resetpassword(request) ---
    Handles the request to reset the user's password. (** currently no token is generated **) Sends an email to the user containing a link to reset the password.
    Directs the user back to reset password page after the request.
"""
def resetpassword(request):
    form = ResetForm(request.POST)
    if form.is_valid():
        try:
            u = User.objects.get(Q(username=request.POST['username']) | Q(email=request.POST['username']))
        except (User.DoesNotExist): #if there is not... redirect to the login page
            return render(request, 'main/resetpassword.html', {
                'error_message': "This username or email does not exist. Did you enter it correctly?",
                'form': form,
            })
        from_user = settings.EMAIL_HOST_USER
        subject = 'Password reset'
        message = resetmail(u.id)
        sender = 'Your web app'
        to = 'yeexin94ay@live.com' #change this to the user's email
        send_mail(subject, message, sender, ['yeexin94ay@live.com'], fail_silently=False)
        print("sending mail...")
        template = loader.get_template('main/resetpassword.html')
        return HttpResponse(template.render({'message': 'An email has been sent to ' + u.email, 'form': form,}, request))
    else:
        template = loader.get_template('main/resetpassword.html')
        return HttpResponse(template.render({'error_message': 'Please fill up the form.', 'form': form,}, request))


"""
    --- resetmail(request) ---
    Returns a HttpResponse that renders the email to be sent for password reset.
"""
def resetmail(user_id):
    u = User.objects.get(id=user_id)
    return loader.render_to_string('main/resetmail.html', {'user': u})


"""
    --- resetauth(request) ---
    Returns a HttpResponse to display the page for user to change their password for password reset.
"""
def resetauth(request, user_id):
    u = User.objects.get(id=user_id)
    form = NewPasswordForm()
    template = loader.get_template('main/resetauth.html')
    return HttpResponse(template.render({'user': u, 'form': form}, request))

"""
    --- resetauthprocess(request) ---
    Handles the request to change the user's password for password reset.
    Returns a HttpResponseRedirect to redirect the user to the login page if the password reset was successful.
    Otherwise, returns a HttpResponse to direct the user back to the change password page.
"""
def resetauthprocess(request, user_id):
    u = User.objects.get(id=user_id)
    form = NewPasswordForm(request.POST)
    if form.is_valid():
        u.password = request.POST['new_password'] #change the password
        u.save()
        return HttpResponseRedirect(reverse('main:login'))
    else:
        template = loader.get_template('main/resetauth.html')
        return HttpResponse(template.render({'user': u, 'form': form, 'error_message': 'Please fill up the form.'}, request))
