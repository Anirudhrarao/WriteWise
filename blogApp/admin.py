from django.contrib import admin
from blogApp.models import UserProfile, BlogPost, Comment, FollowRequest

admin.site.register(UserProfile)
admin.site.register(BlogPost)
admin.site.register(Comment)
admin.site.register(FollowRequest)
