from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def chat(request):
    return render(request, 'chat/chat.html')