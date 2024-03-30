from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages 
from blogApp.models import BlogPost, Comment, Reply
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.auth.models import User
from userApp.models import UserProfile, FollowRequest

def home(request):
    try:
        blogs = BlogPost.objects.all()
        item_per_page = 3
        
        paginator = Paginator(blogs, item_per_page)
        page = request.GET.get('page')
        
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)
            
        context = {
            'blogs': blogs,
            'title': 'home-page',
        }
        return render(request, 'blogApp/home.html', context)
    except Exception as e:
        print(f"Error in home page: {e}")
        messages.error(request, 'An error occurred while loading the home page.')
        return redirect('blogApp:home-page')

def blog_details(request, pk):
    try:
        blog = get_object_or_404(BlogPost, pk = pk)
        comments = Comment.objects.filter(blog_post = blog)
        noOfLikes = blog.liked_by.count()
        noOfComments =  Comment.objects.filter(blog_post = blog).count()
        
        replies = {}
        for comment in comments:
            replies[comment] = comment.replies.all()
        
        # replies = [reply_queryset for reply_queryset in replies.values()]
        comments_with_replies = [(comment, replies.get(comment, [])) for comment in comments]

        context = {
            'title': 'blog-details',
            'blog': blog,
            'comments': comments,
            'noOfLikes': noOfLikes,
            'noOfComments': noOfComments,
            'replies': replies,
            'comments_with_replies': comments_with_replies,
        }
        return render(request, 'blogApp/blog_details.html', context)
    except Exception as e:
        print(f"Error in blog details page: {e}")
        messages.error(request, 'An error occurred while loading the blog details page.')
        return redirect('blogApp:home-page')

@login_required 
def like_blog(request, pk):
    try:
        blog = get_object_or_404(BlogPost, pk=pk)
        if request.user in blog.liked_by.all():
            blog.liked_by.remove(request.user)
            messages.success(request, 'You unliked the blog post.')
        else:
            blog.liked_by.add(request.user)
            messages.success(request, 'You liked the blog post.')
        blog.save()
        return redirect('blogApp:blog-details', pk=pk)
    except Exception as e:
        print(f"Error in liking blog post: {e}")
        messages.error(request, 'An error occurred while liking the blog post.')
        return redirect('blogApp:home-page')

@login_required
def add_comment(request, pk):
    try:
        if request.method == 'POST':
            content = request.POST.get('content')
            blog_post = get_object_or_404(BlogPost, pk=pk)
            if content:
                comment = Comment.objects.create(
                    blog_post=blog_post,
                    author=request.user,
                    content=content,
                )
                return JsonResponse({
                    'author': comment.author.username,
                    'content': comment.content,
                    'publication_date': comment.publication_date.strftime('%B %d, %Y'),
                })
            else:
                return JsonResponse({'error': 'Comment content cannot be empty.'}, status=400)
        else:
            return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    except Exception as e:
        print(f"Error in adding comment: {e}")
        return JsonResponse({'error': 'An error occurred while adding the comment.'}, status=500)
    
@login_required
def create_blog(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            author = request.user
            featured_image = request.FILES.get('featured_image')
            video = request.FILES.get('video')

            if title and content and featured_image:
                blog = BlogPost.objects.create(
                    title=title,
                    content=content,
                    author=author,
                    featured_image=featured_image,
                    video=video,
                )
                messages.success(request, 'Blog post created successfully.')
                return redirect('blogApp:home-page')
            else:
                messages.error(request, 'Title, content, and featured image should not be empty.')
                return redirect('create-blog')
        except Exception as e:
            # Log the exception for debugging
            print(f"An error occurred while creating a blog post: {e}")
            messages.error(request, 'An error occurred while creating the blog post. Please try again later.')
            return redirect('create-blog')
    else:
        return render(request, 'blogApp/create_blog.html')
    
@login_required
def update_blog(request, pk):
    try:
        blog = get_object_or_404(BlogPost, pk=pk)       
        if request.method == 'POST':
            if request.user != blog.author:
                messages.error(request, 'You are not allowed to edit this blog post.')
                return redirect('userApp:profile-page')
            if 'title' in request.POST:
                blog.title = request.POST.get('title')
            if 'content' in request.POST:
                blog.content = request.POST.get('content')
            if 'featured_image' in request.FILES:
                blog.featured_image = request.FILES.get('featured_image')
            blog.save()
            messages.success(request, 'Blog post updated successfully.')
            return redirect('userApp:profile-page', request.user.username)
        else:
            context = {'blog': blog}
            return render(request, 'blogApp/update_blog.html', context)
    except Exception as e:
        print(f"An error occurred while updating a blog post: {e}")
        messages.error(request, 'An error occurred while updating the blog post. Please try again later.')
        return redirect('blogApp:update-blog', pk=pk)

@login_required
def delete_blog(request, pk):
    try:
        blog = get_object_or_404(BlogPost, pk=pk)
        if request.user == blog.author:
            blog.delete()
            messages.success(request,'Blog post deleted successfully.')
        else:
            messages.error(request,'You are not authorized to delete this blog post.')
        return redirect('userApp:profile-page', request.user.username)
    except Exception as e:
        print(f"An error occurred while deleting a blog post: {e}")
        messages.error(request, 'An error occurred while deleting the blog post. Please try again later.')
        return redirect('userApp:profile-page', request.user.username)

def user_search(request):
    if 'q' in request.GET:
        query = request.GET.get('q')
        user_profiles = UserProfile.objects.filter(user__username__icontains=query)
        users = [profile.user for profile in user_profiles]  # Extract User instances from UserProfile instances
        current_user_profile = UserProfile.objects.get(user=request.user)
        current_user_following = current_user_profile.following.values_list('id', flat=True)  # Change 'followers' to 'following'
        follow_requests_sent = FollowRequest.objects.filter(from_user=request.user, to_user__in=users).exists()  # Use users queryset
    else:
        user_profiles = None
        current_user_following = []
        follow_requests_sent = False
    context = {
        'results': user_profiles,
        'current_user_following': current_user_following,
        'follow_requests_sent': follow_requests_sent,
    }
    return render(request, 'blogApp/search_user.html', context)

@login_required
def reply_comment(request, pk):
    try:
        comment = get_object_or_404(Comment, pk=pk)

        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                reply = Reply.objects.create(comment=comment, author=request.user, content=content)
                messages.success(request, 'Reply added successfully.')
                return redirect('blogApp:blog-details', pk=comment.blog_post.pk)
            else:
                messages.error(request, 'Reply content cannot be empty.')
                return redirect('blogApp:blog-details', pk=comment.blog_post.pk)
        else:
            return render(request, 'blogApp/replycomment.html')

    except Exception as e:
        print(f"An error occurred while replying to the comment: {e}")
        messages.error(request, 'An error occurred while replying to the comment.')
        return redirect('blogApp:home-page')