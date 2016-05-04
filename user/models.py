from django.db import models
from django.utils import timezone

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
    description = models.CharField(max_length=200)
    vis = models.PositiveSmallIntegerField(choices=VIS_CHOICES)
    profileImg = models.ImageField(upload_to='pic/', default = 'pic/myeh.jpg')
    bgImg = models.ImageField(upload_to='bg/', default = 'bg/myeh.jpg')  #change to imagefield?
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
    siteusername = models.CharField(max_length=50)
    email = models.EmailField()
    url = models.URLField()
    post_date = models.DateTimeField(auto_now=True)
    usage = models.PositiveSmallIntegerField(choices=USAGE_CHOICES)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    vis = models.PositiveSmallIntegerField(choices=VIS_CHOICES)
    logo = models.ImageField(upload_to='logo/', default = 'bg/myeh.jpg') #change to imagefield?

    def __str__(self):
        return self.sitename

    def was_posted_recently(self):
        return self.post_date >= timezone.now() - datetime.timedelta(days=1)

class Notification(models.Model):
    fromuser = models.PositiveIntegerField()
    touser = models.PositiveIntegerField()
    is_read = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    notif_date = models.DateTimeField(auto_now=True)
    message = models.CharField(max_length=100)

class Connection(models.Model):
    fromuser = models.PositiveIntegerField()
    touser = models.PositiveIntegerField()
