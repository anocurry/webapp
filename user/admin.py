from django.contrib import admin

# Register your models here.
from .models import User, Post, Connection, Notification

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Connection)
admin.site.register(Notification)
