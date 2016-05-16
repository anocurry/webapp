from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.core.urlresolvers import reverse
from django.db.models import Q
import datetime

from PIL import Image
from django.core.files import File
import os
import json

import user.apikeys
import tweepy

from .models import User, Post, Connection, Notification
from .forms import PostForm, AccountForm

# Create your views here.

"""
    --- index(request) ---
    Returns a HttpResponse to display the user's profile.
    If the user is not logged in, the user is redirected to the application main page.
"""
def index(request):
    #display the logged in user here
    u = getLoggedInUser(request)
    if u is None:
        #redirect to the main page if the user is not logged in
        return HttpResponseRedirect(reverse('main:index'))
    posts = getSortedUserPosts(u.id, True, True)
    form = PostForm()
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/index.html')
    return HttpResponse(template.render({'user': u, 'form': form, 'notifNum': notifNum, 'ownprofile': True, 'posts': posts}, request))


"""
    --- getSortedUserPosts(user_id, ownprofile, connected) ---
    Returns a series of posts, sorted by their usage (most used, moderately used, least user, on hiatus)
    Used in index (user's own profile) and search pages.

    Parameters:
        ownprofile  : True if the user is viewing their own profile. False otherwise.
        connected   : True if the user is viewing a connected user. False otherwise.
    (See also: models.py in users)
"""
def getSortedUserPosts(user_id, ownprofile, connected):
    try:
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    if ownprofile: #if user is viewing their own profile, return all posts...
        mostUsed = Post.objects.filter(user_id=u.id, usage=3)
        moderatelyUsed = Post.objects.filter(user_id=u.id, usage=2)
        leastUsed = Post.objects.filter(user_id=u.id, usage=1)
        onHiatus = Post.objects.filter(user_id=u.id, usage=0)
    elif connected: #else if users are connected, return posts which are not private...
        mostUsed = Post.objects.filter(Q(user_id=u.id) &  Q(usage=3) & ~Q(vis=0))
        moderatelyUsed = Post.objects.filter(Q(user_id=u.id) &  Q(usage=2) & ~Q(vis=0))
        leastUsed = Post.objects.filter(Q(user_id=u.id) &  Q(usage=1) & ~Q(vis=0))
        onHiatus = Post.objects.filter(Q(user_id=u.id) &  Q(usage=0) & ~Q(vis=0))
    else: #if user is not viewing their own profile and they're not connected, return only public posts...
        mostUsed = Post.objects.filter(user_id=u.id, usage=3, vis=2)
        moderatelyUsed = Post.objects.filter(user_id=u.id, usage=2, vis=2)
        leastUsed = Post.objects.filter(user_id=u.id, usage=1, vis=2)
        onHiatus = Post.objects.filter(user_id=u.id, usage=0, vis=2)

    posts = {
        'mostUsed': mostUsed,
        'moderatelyUsed' : moderatelyUsed,
        'leastUsed': leastUsed,
        'onHiatus': onHiatus,
    }
    print(posts)
    return posts


"""
    --- newpostform(request) ---
    Returns a HTML page that displays a PostForm.
    Used when the user is displaying their own profile and has selected 'Add a new account'
    Called using AJAX.
    (See also: forms.py)
"""
def newpostform(request):
    form = PostForm()
    template = loader.get_template('user/postform.html')
    return HttpResponse(template.render({'form': form,}, request))


"""
    --- newpostformid(request, post_id) ---
    Returns a HTML page that displays a PostForm, based on the post_id.
    Used when the user is displaying their own profile and has selected the edit button under one of the posts they have.
    Called using AJAX.
    (See also: forms.py)

    Parameters:
        post_id : id of the targeted post. Passed when the user clicks on the edit button.
"""
def newpostformid(request, post_id):
    p = Post.objects.get(id=post_id)
    form = PostForm(instance=p)
    template = loader.get_template('user/postform.html')
    return HttpResponse(template.render({'form': form,}, request))


"""
    --- sitenamefind(request) ---
    Returns a HTML page that displays connected users who have posts with the same sitenames as the user's input. The page is rendered and displayed within the PostForm.
    Returns nothing if there is no connected users who have such posts.
    Called using AJAX whenever the input field of sitename is no longer in focus.
"""
def sitenamefind(request):
    sitename = request.GET['sitename']
    connected_users = getConnectedUsers(request.session['login_id'])
    template = loader.get_template('user/sitenamefind.html')
    have_sameposts = []
    count = 0
    if bool(connected_users):
        for c in connected_users:
            posts = Post.objects.filter(Q(user_id=c.id) & ~Q(vis=0) & Q(sitename__iexact=sitename))
            if posts:
                have_sameposts.append(c)
        count = len(have_sameposts)
        if count > 5: #if more than 5 users, get the first five users only...
            have_sameposts = have_sameposts[:5]
    count = count - 5
    return HttpResponse(template.render({'connectedusers': have_sameposts, 'count': count,'sitename': sitename }, request))


"""
    --- sitenamelist(request) ---
    Returns a series of JSON objects to be used as drop down suggestions when the user is inputting the site name while adding or editing a post. At most 6 items are returned.
    The JSON objects are in the form of a dictionary with their index as the key and { sitename, count } as values.
        sitename    : (case-insensitive) the sitename that contains the characters in the user's input. This value is obtained from the database by checking what sitenames are used by other users.
        count       : the number of users using this sitename in their posts.
    The JSON format is as follows:
    {
        0 {
            sitename    : xxx;
            count       : ###;
        }
        1 {
            sitename    : xxx;
            count       : ###;
        }
        ...
    }
    Called using AJAX whenever there is a keyup event.
"""
def sitenamelist(request):
    sitename = request.GET['sitename']
    sitenamelist = []
    optionlist = {}
    counter = 0
    if sitename != '':
        posts = Post.objects.filter(sitename__contains=sitename)
        for p in posts:
            if p.sitename.lower() not in sitenamelist:
                sitenamelist.append(p.sitename.lower())
                count = Post.objects.filter(sitename__iexact=p.sitename).count()
                optionlist[counter] = {
                    'sitename': p.sitename.lower(),
                    'count': count,
                }
                counter += 1
                #optionlist.append('<option label="'+str(count)+' users">' + p.sitename.lower() +'</option>')
                #optionlist.append('<option>' + p.sitename.lower() +'</option>')
                #optionlist.append(p.sitename.lower())
        if (len(optionlist) > 6): #suggest only 6 items max...
            slicedoptionlist = {}
            for i in range(0, 6):
                slicedoptionlist[i] = optionlist[i]
                #optionlist = optionlist[:7]
            optionlist = slicedoptionlist
    print(optionlist)
    print(json.dumps(optionlist));
    return HttpResponse(json.dumps(optionlist), content_type='application/json')

"""
    --- getLoggedInUser(request) ---
    Returns the logged in User object.
    Returns None if the user is not logged in.
"""
def getLoggedInUser(request):
    uid = request.session.get('login_id')
    try:
        u = User.objects.get(id=uid)
    except (KeyError, User.DoesNotExist):
        return None
    return u

"""
    --- search(request, user_id) ---
    Returns a HTML page that displays the profile of the user, corresponding to the user_id.
    The page is displayed differently for the user's own profile, a connected user and a non-connected user.

    Parameters:
        user_id : the id of the user to be searched.
"""
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

    posts = getSortedUserPosts(user_id, ownprofile, connected)
    return HttpResponse(template.render({'user': u, 'notifNum': notifNum, 'searcheduser': searcheduser, 'ownprofile': ownprofile, 'form': form, 'connected': connected, 'notif': n, 'posts': posts, }, request))


"""
    --- searchuser(request) ---
    Handles the searching request when the user enters a username to be searched.
    Calls search() which returns the HTML page displaying the profile of the user if such user exists.
    Otherwise, returns a HTML page showing that the searched username could not be found.

    Parameters:
        user_id : the id of the user to be searched.
"""
def searchuser(request):
    u = getLoggedInUser(request)
    notifNum = getUnreadNotifNum(request)
    try:
        searcheduser = User.objects.get(username__iexact=request.GET['user_name'])
    except (KeyError, User.DoesNotExist):
        template = loader.get_template('user/searchnotfound.html')
        return HttpResponse(template.render({'user': u, 'notifNum': notifNum,}, request))
    return search(request, searcheduser.id)

def viewaspublic(request):
    return viewasdetails(request, False)

def viewasconnected(request):
    return viewasdetails(request, True)

"""
    --- viewasdetails(request, connected) ---
    Called by viewaspublic and viewasconnected to enable the user to view as public and view as a connected user respectively.
    Returns a HTML page displaying the user's profile. The same HTML page as search() is used.
"""
def viewasdetails(request, connected):
    searcheduser = getLoggedInUser(request)
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/search.html')
    n = None
    posts = getSortedUserPosts(searcheduser.id, False, connected)
    return HttpResponse(template.render({'user': searcheduser, 'notifNum': notifNum, 'searcheduser': searcheduser, 'ownprofile': False, 'connected': connected, 'notif': n, 'posts': posts, 'viewas': True }, request))


"""
    --- settings(request) ---
    Returns a HTML page of the settings page that enables the user to edit their account information. AccountForm is used.
    (See also: forms.py)
"""
def settings(request):
    try:
        uid = request.session.get('login_id')
        u = User.objects.get(id=uid)
    except (KeyError, User.DoesNotExist):
        return HttpResponseRedirect(reverse('main:index'))

    message = getMessage(request, 'settings_success', "Your settings have been successfully changed.")
    notifNum = getUnreadNotifNum(request)
    form = AccountForm(instance=u)
    template = loader.get_template('user/settings.html')
    return HttpResponse(template.render({'form': form, 'user': u, 'notifNum': notifNum, 'message': message}, request))


"""
    --- getMessage(request, sessionName, successMessage) ---
    This function is used in order to display success messages when HttpResponseRedirect() is used.
    Returns the successMessage passed in if the sessionName is a valid session variable. Otherwise, None is returned.
    At the end of this function, the session variable is ensured to be set to False.

    Parameters:
        sessionName     : the name of the session variable that determines whether the message should be displayed.
        successMessage  : the message to be displayed should the session variable is valid.
"""
def getMessage(request, sessionName, successMessage):
    if get_sessionSuccess(request, sessionName):
        message = successMessage
        request.session[sessionName] = False
    else:
        message = None
    return message


"""
    --- get_sessionSuccess(request, name) ---
    Checks whether the session variable is True or False.
    Handles the KeyError exception by returning False if the session variable is not set.

    Parameters:
        name    : name of the session variable to be checked against.
"""
def get_sessionSuccess(request, name):
    try:
        result = request.session[name]
    except KeyError:
        result = False
    return result


"""
    --- customize(request) ---
    Returns a HTML page that displays the customization page, for the user to change their profile image and header image.
"""
def customize(request):
    try:
        uid = request.session.get('login_id')
        u = User.objects.get(id=uid)
    except (KeyError, User.DoesNotExist):
        return HttpResponseRedirect(reverse('main:index'))
    message = getMessage(request, 'profileImg_success', "Your profile image has been successfully updated.")
    if not message:
        message = getMessage(request, 'bgImg_success', "Your header image has been successfully updated.")
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/customize.html')
    return HttpResponse(template.render({'user': u, 'notifNum': notifNum, 'message': message}, request))


"""
    --- editsettings(request) ---
    Handles the editing when the user submits the AccountForm in the settings page.
    Returns a HTML page that displays the settings page and the return message (whether the user's information is successfully updated or an error has occurred).
"""
def editsettings(request):
    #do checking for password first...
    u = getLoggedInUser(request)
    notifNum = getUnreadNotifNum(request)
    form = AccountForm(instance=u)
    if (u.password != request.POST['password']):
        return render(request, 'user/settings.html', {
            'error_message': "Your password was incorrect. Please try again.",
            'form': form,
            'user': u,
            'notifNum': notifNum,
        })
    try:
        u1 = User.objects.get(~Q(id=u.id) & Q(username__iexact=request.POST['username']) | ~Q(id=u.id) & Q(email=request.POST['email']))
    except User.DoesNotExist:
        #if details do not clash, save the user's new settings...
        form = AccountForm(request.POST)
        if form.is_valid():
            u.username = request.POST['username']
            u.email = request.POST['email']
            u.displayname = request.POST['displayname']
            u.description = request.POST['description']
            u.vis = request.POST['vis']
            if (bool(request.POST['new_password'])):
                u.password = request.POST['new_password']
            u.save()
            request.session['settings_success'] = True
            return HttpResponseRedirect(reverse('user:settings'))
        else:
            form = AccountForm(instance=u)
            return render(request, 'user/settings.html', {
                'error_message': "Some error occurred in editing. Please try again.",
                'form': form,
                'user': u,
                'notifNum': notifNum,
            })

    #otherwise, return with an error message
    return render(request, 'user/settings.html', {
        'error_message': "The username or email is already in use. Please try again.",
        'form': form,
        'user': u,
        'notifNum': notifNum,
    })


"""
    --- editsettings(request) ---
    Handles the editing when the user changes their profile image.
    The image is cropped into a square using the either the width or height of the original image, whichever is smaller.
    Returns a HTML page that displays the customization page.
"""
def editprofileimg(request):
    u = getLoggedInUser(request)
    if (bool(request.FILES)):
        pimg = request.FILES['profileImg']
        img = Image.open(pimg)
        #check if the image is a square...
        if (img.width != img.height): #if the image is not a square
            if (img.width > img.height): #crop the width
                offset = (img.width - img.height)//2
                newimg = img.crop((offset, 0, img.width-offset, img.height))
            elif (img.width < img.height): #crop the height
                offset = (img.height - img.width)//2
                newimg = img.crop((0, offset, img.width, img.height-offset))
            newimg.save("C:/Users/user/Documents/GitHub/webapp/media/cropped/pic/" + str(pimg))
            pimg = 'cropped/pic/' + str(pimg) #if cropped, assign a new value to pimg..
        u.profileImg = pimg
        u.save()
        request.session['profileImg_success'] = True
        return HttpResponseRedirect(reverse('user:customize'))
    #if failed, return to user's customize page
    return render(request, 'user/customize.html', {
        'error_message': "Something went wrong. Please try again.",
    })


"""
    --- editbgimg(request) ---
    Handles the editing when the user changes their header image.
    Returns a HTML page that displays the customization page.
"""
def editbgimg(request):
    u = getLoggedInUser(request)
    if (bool(request.FILES)):
        bgimg = request.FILES['bgImg']
        u.bgImg = bgimg
        u.save()
        request.session['bgImg_success'] = True
        return HttpResponseRedirect(reverse('user:customize'))
    #if failed, return to user's customize page
    return render(request, 'user/customize.html', {
        'error_message': "Something went wrong. Please try again.",
    })


"""
    --- notifications(request) ---
    Returns a HTML page that displays the notification page. Displays the unread and read notifications differently.
"""
def notifications(request):
    u = getLoggedInUser(request)
    readnotifs = Notification.objects.filter(Q(fromuser=u.id) & Q(is_accepted=True) & Q(is_read=True) | Q(touser=u.id) & Q(is_read=True)).order_by('-notif_date')
    toread = Notification.objects.filter(Q(fromuser=u.id) & Q(is_accepted=True) & Q(is_read=False) | Q(touser=u.id) & Q(is_accepted=False) & Q(is_read=False)).order_by('-notif_date')
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/notifications.html')
    return HttpResponse(template.render({'user': u, 'readnotifs': readnotifs, 'toread': toread,'notifNum': notifNum}, request))


"""
    --- readnotifs(request) ---
    Sets the is_read attribute of the user's unread notifications to True.
    This function is called using AJAX within the notification page.
"""
def readnotifs(request):
    u = getLoggedInUser(request)
    toread = Notification.objects.filter(Q(fromuser=u.id) & Q(is_accepted=True) & Q(is_read=False) | Q(touser=u.id) & Q(is_accepted=False) & Q(is_read=False))
    for n in toread:
        n.is_read = True
        n.save()
    return HttpResponse("Notifications have been read")


"""
    --- getUnreadNotifNum(request) ---
    Get the number of unread notifications to be displayed in the header of each page.
"""
def getUnreadNotifNum(request):
    u = getLoggedInUser(request)
    if u:
        num = Notification.objects.filter(Q(fromuser=u.id) & Q(is_accepted=True) & Q(is_read=False) |  Q(touser=u.id) & Q(is_accepted=False) & Q(is_read=False)).count()
        return num


"""
    --- newpost(request) ---
    Handles both adding and editing the user's post. If the user chooses to add a new account, a new post is created. Otherwise, if the user chooses to edit an existing account, the targeted post is edited.
    Returns a HttpResponseRedirect to redirect the user to index page when the post has been successfully added or edited.
    Returns a HttpResponse that displays the index page if there is an error message.
"""
def newpost(request):
    u = getLoggedInUser(request)
    posts = getSortedUserPosts(u.id, True, True)
    notifNum = getUnreadNotifNum(request)
    if (request.POST['postid'] != ''): #check if the user is editing an existing post
        try:
            p = Post.objects.get(id=request.POST['postid'])
        except Post.DoesNotExist:
            return render(request, 'user/index.html', {
                'error_message': "This post no longer exists.",
                'user': u,
                'notifNum': notifNum,
                'ownprofile': True,
                'posts': posts,
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
            #p.category = request.POST['category']
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
                'user': u,
                'notifNum': notifNum,
                'ownprofile': True,
                'posts': posts,
            })
    else: #if not, create a new post and add it
        form = PostForm(request.POST, request.FILES)
        print(bool(request.POST['vis']))
        if (bool(request.POST['sitename']) and bool(request.POST['usage']) and bool(request.POST['vis'])):
            if bool(request.FILES): #if the user has uploaded a logo
                l = request.FILES['logo']
            else:
                path = 'logo/default/' + request.POST['sitename'] + '.png'
                if (os.path.exists('media/' + path)): #check if there's a default logo
                    l = path
                else:
                    l = 'logo/default/pizza.png'
            print(l)
            p = u.post_set.create(sitename=request.POST['sitename'], siteusername=request.POST['siteusername'], email=request.POST['email'], url=request.POST['url'], usage=request.POST['usage'], description=request.POST['description'], vis=request.POST['vis'], logo=l)
            return HttpResponseRedirect(reverse('user:index'))
        else:
            return render(request, 'user/index.html', {
                'error_message': "Some errors occurred while adding. Please try again.",
                'form': form,
                'user': u,
                'notifNum': notifNum,
                'ownprofile': True,
                'posts': posts,
            })


"""
    --- deletepost(request) ---
    Handles the user's request to delete an existing post.
    Returns a HttpResponseRedirect to redirect the user to index page when the post has been successfully added or edited.
    Returns a HttpResponse that displays the index page if there is an error message.
"""
def deletepost(request):
    if request.POST['deletepostid']:
        try:
            p = Post.objects.get(id=request.POST['deletepostid'])
        except Post.DoesNotExist:
            return render(request, 'user/index.html', {
                'error_message': "This post no longer exists.",
            })
        p.delete()
        return HttpResponseRedirect(reverse('user:index'))


"""
    --- newnotif(request, user_id) ---
    Creates a new notification (connection request) to the targeted user with id = user_id
    Used when the user selects '+ Connect' on the targeted user's profile page.
    Returns a HttpResponseRedirect to redirect the user to the searched user's profile.

    Parameters:
        user_id : id of the targeted user to send notification to.
"""
def newnotif(request, user_id):
    uid = request.session.get('login_id')
    n=Notification(fromuser=uid, touser=user_id, message='test', notif_date=datetime.datetime.now())
    n.save()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))

"""
    --- cancelnotif(request, user_id) ---
    Deletes a notification (connection request) sent to the targeted user with id = user_id
    Returns a HttpResponseRedirect to redirect the user to the searched user's profile.

    Parameters:
        user_id : id of the targeted user whose notification is to be deleted.
"""
def cancelnotif(request, user_id):
    uid = request.session.get('login_id')
    try:
        n=Notification.objects.filter(fromuser=uid, touser=user_id, is_accepted=False).latest('notif_date')
    except Notification.DoesNotExist:
        return HttpResponseRedirect(reverse('user:search', args=(user_id,)))
    n.delete()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))


"""
    --- connections(request) ---
    Returns a HTML page that displays the connections page. Displays each users together with the posts that have the same sitename as the user's posts.
"""
def connections(request):
    u = getLoggedInUser(request)
    notifNum = getUnreadNotifNum(request)
    template = loader.get_template('user/connections.html')

    connections = Connection.objects.filter(Q(fromuser=u.id) | Q(touser=u.id)) #find if the user is connected with anyone
    if (not bool(connections)): #if there is none, just return the page...
        return HttpResponse(template.render({'user': u, 'notifNum': notifNum}, request))
    #otherwise, get them conected users
    connectedusers = []
    connected_users = getConnectedUsers(u.id)
    for c in connected_users:
        u_posts = u.post_set.all() #get logged in user's all posts
        connected_u_posts = Post.objects.filter(Q(user_id=c.id) & ~Q(vis=0))
        count = connected_u_posts.count()
        sameposts = []
        for p in u_posts:
            #find connected users' non-private posts
            posts = Post.objects.filter(Q(user_id=c.id) & ~Q(vis=0))
            for i in posts:
                if i.sitename.lower() == p.sitename.lower(): #match the site names
                    sameposts.append(i)
        connectedusers.append({
            'connecteduser': c,
            'connecteduser_postcount': count,
            'connecteduser_sameposts': sameposts,
        })
    return HttpResponse(template.render({'user': u, 'notifNum': notifNum, 'connectedusers': connectedusers}, request))

"""
    --- get_status_twitter(request) ---
    Handles request to get the latest tweet of the twitter user defined by screen_name sent through the GET request.
"""
def get_status_twitter(request):
    auth = tweepy.OAuthHandler(user.apikeys.TWITTER_CONSUMER_KEY, user.apikeys.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(user.apikeys.TWITTER_ACCESS_TOKEN, user.apikeys.TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    public_tweets = api.home_timeline()

    screen_name = request.GET['screen_name']
    t = None
    error_message = ""
    try:
        t = api.user_timeline(screen_name)[0]
    except (UnicodeEncodeError, tweepy.TweepError):
        #TweepError is raised for private twitters
        error_message = "Sorry, this account's tweets could not be retrieved."
        pass

    template = loader.get_template('embed/twitter.html')
    return HttpResponse(template.render({'screen_name': screen_name, 'tweet': t, 'ownprofile': True, 'error_message': error_message}, request))


"""
    --- getConnectedUsers(user_id) ---
    Returns an array of User objects that are connected with the user.
"""
def getConnectedUsers(user_id):
    connections = Connection.objects.filter(Q(fromuser=user_id) | Q(touser=user_id))
    if (not bool(connections)): #if there's no connections, return none...
        return None
    connectedusers = []
    for c in connections:
        if (c.fromuser == user_id):
            connected_u = User.objects.get(id=c.touser)
        else:
            connected_u = User.objects.get(id=c.fromuser)
        connectedusers.append(connected_u)
    return connectedusers


"""
    --- newconnect(request, user_id) ---
    Establishes a connection between the user and the targeted user by creating a new connection object in te database. Used when the user selects 'Accept request'.
    Returns a HttpResponseRedirect to redirect the user to the searched user's profile.

    Parameters:
        user_id : id of the targeted user who is to be connected with the user.
"""
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


"""
    --- disconnect(request, user_id) ---
    Deletes the connection established between the user and the targeted user by deleting the connection object in te database. Used when the user selects 'Disconnect'
    Returns a HttpResponseRedirect to redirect the user to the searched user's profile.

    Parameters:
        user_id : id of the targeted user who is to be disconnected with the user.
"""
def disconnect(request, user_id):
    uid = request.session.get('login_id')
    c = isConnected(request, user_id)
    if c is None:
        #do nothing
        return HttpResponseRedirect(reverse('user:search', args=(user_id,)))
    c.delete()
    return HttpResponseRedirect(reverse('user:search', args=(user_id,)))


"""
    --- isConnected(request, user_id) ---
    Returns a Connection object if the user is connected with the targeted user. Otherwise, None is returned.

    Parameters:
        user_id : id of the targeted user who is to be checked if they are connected with the user.
"""
def isConnected(request, user_id):
    uid = request.session.get('login_id')
    try:
        c = Connection.objects.get((Q(fromuser=uid) & Q(touser=user_id)) | (Q(fromuser=user_id) & Q(touser=uid))) #find if they have established a connection
    except Connection.DoesNotExist:
        return None
    return c


"""
    --- findNotif(request, user_id) ---
    Returns an integer to check if there is any notification sent to or received from the targeted user, to render the targeted user's profile differently.

    Parameters:
        user_id : id of the searched user.
"""
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


"""
    --- custom(request) ---
    Returns a HTML page that allows the user to create custom widgets.
"""
def custom(request):
    try:
        uid = request.session.get('login_id')
        u = User.objects.get(id=uid)
    except (KeyError, User.DoesNotExist):
        return HttpResponseRedirect(reverse('main:index'))

    notifNum = getUnreadNotifNum(request)
    posts = Post.objects.filter(Q(user_id=u.id) & ~Q(url=''))
    template = loader.get_template('user/custom.html')
    return HttpResponse(template.render({'posts': posts, 'user': u, 'notifNum': notifNum,}, request))

"""
    --- custom(request) ---
    Returns a HTML page that renders the custom widgets based on the user's request.
    Called using AJAX when the user submits the form in custom.html.
"""
def customsubmit(request):
    print("### PRINTING CUSTOM SUBMIT ### ")
    posts = []
    choices = request.GET['customchoice'].split(", ")
    for i in choices:
        posts.append(Post.objects.get(id=int(i)))
    print(choices)
    template = loader.get_template('user/customwidgethtml.html')
    return HttpResponse(template.render({'posts': posts, }, request))


"""
    --- logout(request) ---
    Logs out the user and redirects the user to the index page of the application.
"""
def logout(request):
    try:
        del request.session['login_id']
        del request.session['loggedin']
        #do something else
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('main:index'))
