from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.

import json
import requests

# 어떻게 호출하냐면 /profile/?username={username} (GET 방식)
def profile(request):
    username = request.GET['username']
    url = 'https://api.github.com/users/%s' % username
    response = requests.get(url).json()
    return render(request, 'git_profile/profile.html',{
        'name': response['login'],
        'profile_img_url': response['avatar_url'],
        'info': response['bio']
    })
