from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to="profile/pictures", default="images\man.png", null=True, blank=True)
    bio = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    following = models.ManyToManyField(User, related_name='followers', blank=True)
    
    def __str__(self):
        return self.user.username


class FollowRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Follow request from {self.from_user.username} to {self.to_user.username}"

class Status(models.Model):
    user = models.ForeignKey(UserProfile, related_name='statuses', on_delete=models.CASCADE)
    content = models.TextField(blank=True)  
    image = models.ImageField(upload_to="status/images", null=True, blank=True)  
    video = models.FileField(upload_to="status/videos", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.user.username}'s status at {self.created_at}"