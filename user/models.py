from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

"""
    User:
    - Represents the accounts registered by the users within the application.

    Attributes:
    - username (unique)
    - password
    - email (unique)
    - displayname (not unique)
    - description
    - vis (integer field - public/1 or private/0)
    - profileImg
    - bgImg
    - useBg (unused attribute)
"""
class User(models.Model):
    VIS_CHOICES=(
        (1, 'Public'),
        (0, 'Private'),
    )
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField()
    displayname = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    vis = models.PositiveSmallIntegerField(choices=VIS_CHOICES, default=1)
    profileImg = models.ImageField(upload_to='pic/', default = 'pic/default.jpg')
    bgImg = models.ImageField(upload_to='bg/', default = 'bg/default.jpg')  #change to imagefield?
    useBg = models.BooleanField()

    def __str__(self):
        return self.username

"""
    Post:
    - Represents the accounts of other site domains added by the users into their profiles.

    Attributes:
    - user (reference to user's ID as foreign key)
    - sitename (name of the site domain of the account added)
    - siteusername (username used on that site domain)
    - email (email used on that site domain - stored as a record of the user's login credential)
    - url
    - post_date (date of the latest update of the post)
    - usage (integer field - Most used/3, Moderately used/2, Least used/1, On hiatus/0)
    - description
    - vis (integer field - public/2, reserved/1, private/0)
    - logo
"""
class Post(models.Model):
    VIS_CHOICES=(
        (2, 'Public'),
        (1, 'Reserved'),
        (0, 'Private'),
    )
    USAGE_CHOICES=(
        (3, 'Most used'),
        (2, 'Moderately used'),
        (1, 'Least used'),
        (0, 'On hiatus'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sitename = models.CharField(max_length=50)
    siteusername = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    url = models.URLField(blank=True)
    post_date = models.DateTimeField(auto_now=True)
    usage = models.PositiveSmallIntegerField(choices=USAGE_CHOICES, default=3)
    category = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=100, blank=True)
    vis = models.PositiveSmallIntegerField(choices=VIS_CHOICES, default=2)
    logo = models.ImageField(upload_to='logo/', default = 'logo/default/pizza.png') #change to imagefield?

    def __str__(self):
        return str(self.id) + ' ' + self.sitename

    def was_posted_recently(self):
        return self.post_date >= timezone.now() - datetime.timedelta(days=1)

    def has_url(self):
        return bool(self.url)

    def has_email(self):
        return bool(self.email)

    def formatted_post_date(self):
        month = self.post_date.strftime('%b')
        day = str(self.post_date.day)
        result = month + " " + day
        return result


"""
    Notification
    - Generated when users send others a connection request or a connection request has been accepted.

    Attributes:
    - fromuser (id of the user who sent the connection request)
    - touser (id of the user who received the connection request)
    - is_read (boolean field)
    - is_accepted (boolean field)
    - notif_date (date of sending the connection request. This attribute is updated when the connection request is accepted. The new value is the date of which the request is accepted)
    - message (unused attribute)
"""
class Notification(models.Model):
    fromuser = models.PositiveIntegerField()
    touser = models.PositiveIntegerField()
    is_read = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    notif_date = models.DateTimeField(default=datetime.datetime.now())
    message = models.CharField(max_length=100)
    def __str__(self):
        return str(self.notif_date)

    def from_username(self):
        u = User.objects.get(id=self.fromuser)
        return u.username

    def to_username(self):
        u = User.objects.get(id=self.touser)
        return u.username

    def from_user_profileimg(self):
        u = User.objects.get(id=self.fromuser)
        return u.profileImg

    def to_user_profileimg(self):
        u = User.objects.get(id=self.touser)
        return u.profileImg


"""
    Connection
    - Represents the establishment of connection between two users.

    Attributes:
    - fromuser (id of the user who sent the connection request)
    - touser (id of the user who received and accepted the connection request)
"""
class Connection(models.Model):
    fromuser = models.PositiveIntegerField()
    touser = models.PositiveIntegerField()
