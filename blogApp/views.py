from datetime import datetime
from django.contrib import messages 
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt 
from django.shortcuts import render, get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from blogApp.models import UserProfile, BlogPost, Comment, FollowRequest 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def home(request):
    """
    View function for the home page, displaying a paginated list of blog posts.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered response for the home page.
    """
    try:
        blogs_list = BlogPost.objects.all()
        items_per_page = 3

        paginator = Paginator(blogs_list, items_per_page)
        page = request.GET.get('page')

        # Count pending follow requests if the user is authenticated
        if request.user.is_authenticated:
            numberOfRequest = FollowRequest.objects.filter(to_user=request.user, is_pending=True).count()
        else:
            numberOfRequest = 0

        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        context = {
            'title': 'Home Page',
            'blogs': blogs,
            'numberOfRequest': numberOfRequest,
        }
        return render(request, 'home.html', context)

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in home page: {e}")
        messages.error(request, 'An error occurred while loading the home page.')
        return redirect('home-page')
    

@login_required
def blog_details(request, pk):
    """
    View function for displaying details of a specific blog post.

    Parameters:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the BlogPost object to be displayed.

    Returns:
        HttpResponse: Rendered response for the blog details page.
    """
    try:
        blog_details = get_object_or_404(BlogPost, pk=pk)
        comments = Comment.objects.filter(blog_post=blog_details)

        context = {
            'blog_details': blog_details,
            'comments': comments,
        }
        return render(request, 'blog_details.html', context)

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in blog details page: {e}")
        messages.error(request, 'An error occurred while loading the blog details page.')
        return redirect('home-page')

@login_required
def delete_post(request, pk):
    """
    View function for deleting a blog post.

    Parameters:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the BlogPost object to be deleted.

    Returns:
        HttpResponse: Redirect to the user's profile page after deleting the blog post.
        
    Raises:
        Http404: If the requested BlogPost object does not exist.
    """
    try:
        blog = get_object_or_404(BlogPost, pk=pk)

        # Ensure that the logged-in user is the author of the blog post
        if request.user == blog.author:
            blog.delete()
            messages.success(request, 'Blog post deleted successfully.')
        else:
            messages.error(request, 'You are not authorized to delete this blog post.')

        return redirect('profile_page')

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in deleting blog post: {e}")
        messages.error(request, 'An error occurred while deleting the blog post.')
        return redirect('home-page')
    
@login_required
def profile_page(request):
    """
    View function for displaying the user's profile page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered response for the user's profile page.
    """
    try:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        user_posts = BlogPost.objects.filter(author=user)
        numberOfRequest = FollowRequest.objects.filter(to_user=request.user, is_pending=True).count()

        context = {
            'title': 'Profile Page',
            'user': user,
            'user_profile': user_profile,
            'user_posts': user_posts,
            'post_count': user_posts.count(),
            'users_followers': user_profile.followers.count(),
            'users_following': user_profile.following.count(),
            'followers': user_profile.followers.all(),
            'numberOfRequest': numberOfRequest,
        }

        return render(request, 'profile_page.html', context)

    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile does not exist.')
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in profile page: {e}")
        messages.error(request, 'An error occurred while loading the profile page.')

    return redirect('home-page')

def signin_page(request):
    """
    View function for handling user sign-in.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered response for the sign-in page or redirection to other pages.

    Notes:
        If the request method is POST, the function attempts to authenticate the user.
        If successful, the user is logged in, and a success message is displayed.
        If unsuccessful, an error message is displayed, and the user is redirected to the sign-in page.

        If the request method is not POST, the function renders the sign-in page.

    Raises:
        User.DoesNotExist: If the provided username does not exist during the sign-in attempt.
        Exception: For other unexpected errors during the sign-in process.
    """
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Check if the user exists
            if not User.objects.filter(username=username).exists():
                messages.error(request, 'User does not exist.')
                return redirect('register-page')

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('profile-page')
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('register-page')

        return render(request, 'login_page.html')

    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('register-page')
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in signin page: {e}")
        messages.error(request, 'An error occurred during sign-in.')
        return redirect('home-page')

@login_required
def signout(request):
    """
    View function for handling user logout.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirect to the home page after successful logout.
    """
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('home-page')

@login_required
def add_comment(request, blog_id):
    """
    View function for adding a comment to a blog post.

    Parameters:
        request (HttpRequest): The HTTP request object.
        blog_id (int): The primary key of the BlogPost object to which the comment is added.

    Returns:
        HttpResponse: Redirect to the blog page after successfully adding the comment.

    Notes:
        - The function expects a POST request to add a comment.
        - If the comment content is provided, it creates a new Comment object.
        - Success and error messages are displayed accordingly.
        - If the request is not a POST request, it redirects to the home page.

    Raises:
        Http404: If the requested BlogPost object does not exist.
    """
    if request.method == 'POST':
        content = request.POST.get('content')
        user = request.user 
        blog_post = get_object_or_404(BlogPost, pk=blog_id)
        
        if content:
            Comment.objects.create(
                blog_post=blog_post,
                author=user,
                content=content,
            )
            messages.success(request, 'Comment added successfully.')
            return redirect('blog-page', pk=blog_id)
        else:
            messages.error(request, 'Comment content cannot be empty.')
            return redirect('blog-page', pk=blog_id)
    
    messages.error(request, 'Only post requests are allowed.')
    return redirect('home')

@login_required
def create_post(request):
    """
    View function for creating a new blog post.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered response for the create-post page or redirect to the user's profile page.

    Notes:
        - The function handles both GET and POST requests.
        - If the request method is POST, it attempts to create a new BlogPost object.
        - It retrieves the title, content, and featured image from the request.
        - If all required fields are provided, it creates a new BlogPost object.
        - Success and error messages are displayed accordingly.
        - If the request method is not POST, it renders the create_post.html template.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        featured_image = request.FILES.get('featured_image')
        if title and content and featured_image:
            blog_post = BlogPost.objects.create(
                title=title,
                content=content,
                author=request.user,
                featured_image=featured_image,
            )
            messages.success(request, 'Blog post created successfully.')
            return redirect('profile-page')
        else:
            messages.error(request, 'Title, content, and featured image should not be empty.')
            return redirect('create-post')
    
    return render(request, 'create_post.html')

@login_required
def update_post(request, blog_id):
    try:
        blog_post = get_object_or_404(BlogPost, pk=blog_id)
        if request.method == 'POST':
            if request.user != blog_post.author:
                messages.error(request, 'You are not allowed to edit this blog post.')
                return redirect('profile-page')
            if 'title' in request.POST:
                blog_post.title = request.POST['title']
            if 'content' in request.POST:
                blog_post.content = request.POST['content']
            if 'featured_image' in request.FILES:
                blog_post.featured_image = request.FILES['featured_image']
            blog_post.save()
            messages.success(request, 'Blog post updated successfully.')
            return redirect('profile-page')
        return render(request, 'update_post.html',{'blog_post':blog_post})
    except Exception as e:
        raise e 

@login_required
def update_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if request.method == 'POST':
            if 'bio' in request.POST:
                user_profile.bio = request.POST['bio']
            if 'website' in request.POST:
                user_profile.website = request.POST['website']
            if 'profile_picture' in request.FILES:
                user_profile.profile_picture = request.FILES['profile_picture']

            # Check if the checkbox is present in the request.POST
            # If yes, set is_private to True; otherwise, set it to False
            user_profile.is_private = 'is_private' in request.POST

            user_profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile-page')
        return render(request, 'update_profile.html', {'user_profile': user_profile})
    except Exception as e:
        raise e

        
        return render(request, 'update_profile.html', {'user_profile': user_profile})
    except Exception as e:
        # Handle the exception appropriately (log, display a message, etc.)
        messages.error(request, 'An error occurred while updating the profile.')
        return redirect('profile-page')
            
@login_required
def search_user_profile(request):
    try:
        query = request.GET.get('q')
        users = User.objects.none()  # Default empty queryset

        if query:
            users = User.objects.filter(username__icontains=query)

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in searching user profile: {e}")
        messages.error(request, 'An error occurred while searching user profiles.')

    return render(request, 'search_users.html', {'users': users, 'query': query})

@login_required
def like_blog(request, blog_id):
    try:
        blog_post = get_object_or_404(BlogPost, pk=blog_id)
        user = request.user

        if user in blog_post.liked_by.all():
            blog_post.likes_count -= 1
            blog_post.liked_by.remove(user)
        else:
            blog_post.likes_count += 1
            blog_post.liked_by.add(user)

        blog_post.save()
        return redirect('blog-page', pk=blog_id)

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in liking blog post: {e}")
        messages.error(request, 'An error occurred while liking the blog post.')
        return redirect('home-page')


@login_required
def user_profile(request, username):
    viewed_user_profile = get_object_or_404(UserProfile, user__username=username)
    user_posts = BlogPost.objects.filter(author=viewed_user_profile.user)
    is_following = False
    can_view_profile = False
    follow_request_exists = False

    if request.user.is_authenticated:
        current_user_profile = UserProfile.objects.get(user=request.user)
        is_following = viewed_user_profile.user in current_user_profile.following.all()
        can_view_profile = not viewed_user_profile.is_private or is_following
        follow_request_exists = FollowRequest.objects.filter(
            from_user=request.user, to_user=viewed_user_profile.user, is_pending=True
        ).exists()

    context = {
        'viewed_user_profile': viewed_user_profile,
        'is_following': is_following,
        'can_view_profile': can_view_profile,
        'user_posts': user_posts,
        'post_count': user_posts.count(),
        'users_followers': viewed_user_profile.followers.count(),
        'users_following': viewed_user_profile.following.count(),
        'followers': viewed_user_profile.followers.all(),
        'follow_request_exists': follow_request_exists,
    }

    return render(request, 'user_profile.html', context)




def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            user = User.objects.create_user(username=username, email=email, password=password)
            user_profile = UserProfile.objects.create(user=user)
            user_profile.save()
            messages.success(request, f"Welcome, {user}! Your registration was successful.")
            return redirect('register-page')
        else:
            messages.error(request, "Password and confirm password do not match.")
            return redirect('register-user')
    return render(request, 'registration_page.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        user = request.user
        
        if not user.check_password(old_password):
            messages.error(request, 'Old password is incorrect.')
            return redirect('change_password')
        
        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        
        user.set_password(new_password1)
        user.save()
        
        user = authenticate(username=user.username, password=new_password1)
        login(request, user)
        
        messages.success(request, 'Password changed successfully.')
        return redirect('profile-page')
    
    return render(request, 'change_password.html')


@login_required
def notification(request):
    numberOfRequest = FollowRequest.objects.filter(to_user=request.user, is_pending=True).count()
    allRequest = FollowRequest.objects.filter(to_user=request.user)
    context = {
        'numberOfRequest': numberOfRequest,
        'allRequest': allRequest
    }
    return render(request, 'notification_template.html', context)

@login_required
def follow(request, username):
    user_to_follow = get_object_or_404(UserProfile, user__username=username)
    current_user_profile = request.user.userprofile

    if user_to_follow.user in current_user_profile.following.all():
        messages.warning(request, 'You are already following this user.')
    else:
        # Check if a follow request already exists
        follow_request_exists = FollowRequest.objects.filter(from_user=request.user, to_user=user_to_follow.user).exists()

        if follow_request_exists:
            messages.info(request, 'You have already sent a follow request to this user.')
        else:
            # Create a follow request
            follow_request = FollowRequest.objects.create(from_user=request.user, to_user=user_to_follow.user)
            messages.success(request, f'Follow request sent to {user_to_follow.user.username}. Waiting for approval.')

    return redirect('user_profile', username=username)

@login_required
def unfollow(request, username):
    user_to_unfollow = get_object_or_404(UserProfile, user__username=username)
    current_user_profile = request.user.userprofile
    
    if user_to_unfollow.user in current_user_profile.following.all():
        current_user_profile.following.remove(user_to_unfollow.user)
        messages.success(request, f'You have unfollowed {username}.')
    else:
        messages.info(request, f'You were not following {username}.')
    
    return redirect('user_profile', username=username)

@login_required
def accept_follow_request(request, follow_request_id):
    follow_request = get_object_or_404(FollowRequest, pk=follow_request_id)

    if follow_request.to_user == request.user:
        # Update the follow request status
        follow_request.is_pending = False
        follow_request.is_accepted = True
        follow_request.save()

        # Add the follower to the current user's following list
        request.user.userprofile.followers.add(follow_request.from_user)
        # Add the current user to the follower's followers list
        follow_request.from_user.userprofile.following.add(request.user)
        follow_request.delete()
        messages.success(request, f'You have accepted the follow request of {follow_request.from_user.username}.')
        
    else:
        messages.error(request, 'You do not have permission to accept this follow request.')

    return redirect('notifications')


@login_required
def reject_follow_request(request, follow_request_id):
    follow_request = get_object_or_404(FollowRequest, pk=follow_request_id)

    if follow_request.to_user == request.user:
        # Delete the follow request
        follow_request.delete()

        messages.success(request, f'You have rejected the follow request from {follow_request.from_user.username}.')
    else:
        messages.error(request, 'You do not have permission to reject this follow request.')

    return redirect('notifications')



