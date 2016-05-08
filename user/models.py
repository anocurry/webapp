from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class User(models.Model):
    VIS_CHOICES=(
        (0, 'Private'),
        (1, 'Public'),
    )
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField()
    displayname = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    vis = models.PositiveSmallIntegerField(choices=VIS_CHOICES)
    profileImg = models.ImageField(upload_to='pic/', default = 'pic/default.jpg')
    bgImg = models.ImageField(upload_to='bg/', default = 'bg/default.jpg')  #change to imagefield?
    useBg = models.BooleanField()

    def __str__(self):
        return self.username


class Post(models.Model):
    VIS_CHOICES=(
        (0, 'Private'),
        (1, 'Reserved'),
        (2, 'Public'),
    )
    USAGE_CHOICES=(
        (0, 'On hiatus'),
        (1, 'Least used'),
        (2, 'Moderately used'),
        (3, 'Most used'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sitename = models.CharField(max_length=50)
    siteusername = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    url = models.URLField(blank=True)
    post_date = models.DateTimeField(auto_now=True)
    usage = models.PositiveSmallIntegerField(choices=USAGE_CHOICES)
    category = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=100, blank=True)
    vis = models.PositiveSmallIntegerField(choices=VIS_CHOICES)
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

class Connection(models.Model):
    fromuser = models.PositiveIntegerField()
    touser = models.PositiveIntegerField()
