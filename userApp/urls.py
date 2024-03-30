from django.urls import path
from userApp.views import (
    profile_page,
    register_user,
    login_user,
    logout_view,
    send_follow_request,
    accept_follow_request,
    reject_follow_request,
    update_profile,
    follow_request,
    unfollow,
    remove_followers,
    change_password,
    )

app_name = 'userApp'

urlpatterns = [
    path("<str:username>/profile/", profile_page, name="profile-page"),
    path('register/', register_user, name="register-page"),
    path('login/', login_user, name="login-page"),
    path('logout/', logout_view, name="logout-view"),
    path('send_request_to/<str:username>/',send_follow_request, name="send-request"),
    path('accept_request/<int:request_id>/', accept_follow_request, name="accept-request"),
    path('reject_request/<int:request_id>/', reject_follow_request, name="reject-request"),
    path('update_profile/<str:username>/', update_profile, name="update-profile"),
    path('follow_requests/', follow_request, name="follow-request"),
    path('unfollow/<str:username>/', unfollow, name="unfollow-request"),
    path('remove_follower/<str:username>/', remove_followers, name="remove-follower"),
    path('change_password/', change_password, name="change-password"),
]
