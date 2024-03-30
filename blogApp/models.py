from django.db import models
from django.contrib.auth.models import User

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete = models.SET_NULL, null=True, related_name="blog_posts")
    publication_date = models.DateTimeField(auto_now_add=True)
    featured_image = models.ImageField(upload_to="blog/images", blank=True, null=True)
    video = models.FileField(upload_to="blog/videos", blank=True, null=True)
    # likes_count = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    
    def __str__(self):
        return self.title 
    
    def comment_count(self):
        return self.comments.count()

class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete = models.CASCADE,  related_name="comments")
    author = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on '{self.blog_post.title}'"

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = 'Replies'
        
    def __str__(self):
        return f"Reply by {self.author.username} to comment '{self.comment}'"