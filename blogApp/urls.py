from django.urls import path
from blogApp.views import (
    home,
    blog_details,
    like_blog,
    add_comment,
    create_blog,
    update_blog,
    delete_blog,
    user_search,
    reply_comment,
    )

app_name = 'blogApp'

urlpatterns = [
    path('', home, name='home-page'),
    path('<int:pk>/', blog_details, name='blog-details'),
    path('<int:pk>/like/', like_blog, name='like-toggle'),
    path('<int:pk>/comment/', add_comment, name='comment-blog'),
    path('create/', create_blog, name='create-blog'),
    path('<int:pk>/update/', update_blog, name='update-blog'),
    path('<int:pk>/delete/', delete_blog, name='delete-blog'),
    path('search/', user_search, name='user-search'),
    path('comment/<int:pk>/reply/', reply_comment, name='reply'),
]
