from django.contrib import admin
from django.utils.html import format_html
from userApp.models import UserProfile, FollowRequest, Status

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('profile_image', 'user', 'is_private')
    list_filter = ('is_private',)
    search_fields = ('user__username', 'bio')
    readonly_fields = ('user',)
    
    def profile_image(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />'.format(obj.profile_picture.url))
        else:
            return "No Image"
    profile_image.short_description = 'Profile Picture'

@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'is_accepted')
    list_filter = ('is_accepted',)
    search_fields = ('from_user__username', 'to_user__username')

    def from_user(self, obj):
        return obj.from_user.username
    from_user.short_description = 'From User'

    def to_user(self, obj):
        return obj.to_user.username
    to_user.short_description = 'To User'

admin.site.register(Status)