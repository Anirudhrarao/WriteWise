from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def default_profile_picture():
    return f"profile/pictures/{timezone.now().strftime('%Y%m%d%H%M%S')}.png"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile/pictures', default=default_profile_picture, blank=True)
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)    
    is_private = models.BooleanField(default=False)
    followers = models.ManyToManyField(User, related_name="following", blank=True)
    following = models.ManyToManyField(User, related_name="followers", blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class FollowRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_requests_sent")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_requests_received")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_pending = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f"{self.from_user.username} to {self.to_user.username}"


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="blog_posts")
    publication_date = models.DateTimeField(auto_now_add=True)
    featured_image = models.ImageField(upload_to="blog/images", blank=True, null=True)
    likes_count = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name="liked_posts", blank=True, symmetrical=False)
    
    def __str__(self):
        return self.title

    def comment_count(self):
        return self.comments.count()

class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on '{self.blog_post.title}'"
