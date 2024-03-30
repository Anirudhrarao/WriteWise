from django.contrib import admin
from blogApp.models import BlogPost, Comment, Reply

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'comment_count')
    list_filter = ('author', 'publication_date')
    search_field = ('title', 'content')
    readonly_fields = ('publication_date', 'comment_count')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'author', 'publication_date')
    list_filter = ('blog_post__title', 'author', 'publication_date')
    search_fields = ('content',)
    readonly_fields = ('publication_date',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('blog_post', 'author')

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('comment', 'author', 'publication_date')
    list_filter = ('comment__blog_post__title', 'author', 'publication_date')
    search_fields = ('content',)
    readonly_fields = ('publication_date',)