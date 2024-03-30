from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages 
from blogApp.models import BlogPost, Comment
from userApp.models import UserProfile, FollowRequest, Status
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
import json

@login_required
def profile_page(request, username):
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        users_blogs = BlogPost.objects.filter(author=user)
        followers = profile.followers.all()
        following = profile.following.all()
        
        context = {
            'title': 'Profile-page',
            'profile': profile,
            'users_blogs': users_blogs,
            'followers': followers,
            'following': following,
        }
        
        return render(request, 'userApp/profile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile does not exist.')
        return redirect('blogApp:home-page')
    except Exception as e:
        print(f"Error in profile page: {e}")
        messages.error(request, 'An error occurred while loading the profile page.')
        return redirect('blogApp:home-page')
    
def register_user(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password == confirm_password:
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already exists.")
                    return redirect('userApp:register-page')
                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already exists.")
                    return redirect('userApp:register-page')
                
                user = User.objects.create_user(username=username, email=email, password=password)
                UserProfile.objects.create(user=user)
                
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                
                messages.success(request, f"Welcome, {user.username}! Your registration was successful.")
                return redirect('userApp:profile-page', username=user.username)
            else:
                messages.error(request, "Password and confirm password do not match.")
                return redirect('userApp:register-page')
        return render(request, 'userApp/register.html')
    except IntegrityError as e:
        messages.error(request, "An error occurred during registration. Please try again.")
        return redirect('userApp:register-page')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('userApp:register-page')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('userApp:profile-page', user.username)
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('userApp:login-page')

    return render(request, 'userApp/login.html')

@login_required
def logout_view(request):
    try:
        logout(request)
        messages.success(request, 'Logout successful.')
    except Exception as e: 
        print(f"Error occurred during logout: {e}")
        messages.error(request, 'An error occurred during logout. Please try again.')
    return redirect('blogApp:home-page')
        
@login_required
def send_follow_request(request, username):
    receiver_profile = get_object_or_404(UserProfile, user__username=username)

    if receiver_profile.user.profile.is_private:
        # Check if a follow request already exists
        existing_request = FollowRequest.objects.filter(from_user=request.user, to_user=receiver_profile.user).exists()
        if existing_request:
            messages.info(request, 'You have already sent a follow request. Please wait for the recipient to accept it.')
        else:
            # Create a new follow request
            FollowRequest.objects.create(from_user=request.user, to_user=receiver_profile.user)
            messages.success(request, 'Follow request sent successfully.')
    else:
        # If profile is public, directly add follower
        receiver_profile.user.profile.followers.add(request.user)
        request.user.profile.following.add(receiver_profile.user)
        messages.success(request, 'You are now following this user.')

    return redirect('userApp:profile-page', username=username)

@login_required
def accept_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, pk=request_id)
    if request.user != follow_request.to_user:
        messages.error(request, "You are not authorized to accept this follow request.")
        return redirect('blogApp:home-page')
    
    follow_request.is_accepted = True
    follow_request.save()
    
    # Add the sender to the receiver's followers
    follow_request.to_user.profile.followers.add(follow_request.from_user)
    # Add the receiver to the sender's following
    follow_request.from_user.profile.following.add(follow_request.to_user)
    follow_request.delete()
    messages.success(request, f"You have accepted the follow request from {follow_request.from_user.username}.")
    return redirect('userApp:profile-page', username=request.user.username)
    

@login_required
def reject_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, pk=request_id)
    if request.user != follow_request.to_user:
        messages.error(request, "You are not authorized to reject this follow request.")
        return redirect('blogApp:home-page')
    
    # Delete the follow request
    follow_request.delete()
    
    messages.success(request, f"You have rejected the follow request from {follow_request.from_user.username}.")
    return redirect('userApp:profile-page', username=request.user.username)

@login_required
def update_profile(request, username):
    try:
        user_profile = get_object_or_404(UserProfile, user__username=username)
        if request.user != user_profile.user:
            messages.error(request, 'You do not have permission to edit another user\'s profile.')
            return redirect('blogApp:home-page')
        if request.method == 'POST':
            profile_picture = request.FILES.get('profile_picture')
            bio = request.POST.get('bio')
            is_private = request.POST.get('is_private') == 'on'  
            
            if profile_picture:
                user_profile.profile_picture = profile_picture
            if bio:
                user_profile.bio = bio
            user_profile.is_private = is_private  
            
            user_profile.save()  
            messages.success(request, 'Profile updated successfully.')
            return redirect('userApp:profile-page', username=username)
        
        context = {'user_profile': user_profile}
        return render(request, 'userApp/update_profile.html', context)
    
    except Exception as e:
        messages.error(request, 'An error occurred while updating the profile.')
        print(f"Error updating profile: {e}")
        return redirect('userApp:profile-page', username=username)
    
@login_required
def follow_request(request):
    try:
        follow_requests = FollowRequest.objects.filter(to_user=request.user, is_accepted=False)
        context = {
            'follow_requests': follow_requests
        }
        return render(request, 'userApp/follow_requests.html', context=context)
    except Exception as e: 
        messages.error(request, f"Failed to retrieve follow requests: {str(e)}")
        return redirect('userApp:profile-page', request.user.username)

@login_required
def unfollow(request, username):
    user_profile = get_object_or_404(UserProfile, user__username = username)
    
    request.user.profile.following.remove(user_profile.user)
    
    user_profile.followers.remove(request.user)
    
    request.user.profile.save()
    
    user_profile.save()
    
    messages.success(request, f"You have unfollowed {user_profile.user.username}.")
    
    return redirect('userApp:profile-page', username=username)


@login_required
def remove_followers(request, username):
    user_profile = get_object_or_404(UserProfile, user__username = username)
    
    request.user.profile.followers.remove(user_profile.user)
    
    user_profile.following.remove(request.user)
    
    request.user.profile.save()
    
    user_profile.save()
    
    messages.success(request, f"You have removed {user_profile.user.username}")
    
    return redirect('userApp:profile-page', username=request.user.username)

@login_required
def change_password(request):
    try:
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if not request.user.check_password(old_password):
                messages.error('Invalid old password')
                return redirect('userApp:change-password')
            
            if password != confirm_password:
                messages.error('password and confirm password does not match.')
                return redirect('userApp:change-password')
            
            request.user.set_password(password)
            request.user.save()
            
            user =  authenticate(username=request.user.username, password=password)
            login(request, user)
            
            messages.success(request, 'Password changed Successfully')
            return redirect('userApp:profile-page', username=user.username)
        return render(request, 'userApp/change_password.html')
    except Exception as e:
        raise e
    