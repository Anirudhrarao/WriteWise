from userApp.models import FollowRequest, UserProfile
import json

def notification_count(request):
    try:
        if request.user.is_authenticated:
            no_of_request = FollowRequest.objects.filter(to_user=request.user, is_accepted=False).count()
        else:
            no_of_request = 0
    except Exception as e:
        no_of_request = 0
    
    return {'notification_count': no_of_request}
