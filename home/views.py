from django.shortcuts import render
from django.http import HttpResponse
import requests
from datetime import datetime, timedelta
# Create your views here.
def index(request):
    return render(request, 'home/mainpage.html', {})

def rankByDate(option):
    today = datetime.today()
    if option=='day':
        diff = timedelta(days=1)
    elif option=='week':
        diff = timedelta(days=today.weekday())
    elif option=='month':
        diff = timedelta(days=today.day)
    target = str(today - diff).split()[0]
    
    commitList = Commit.objects.filter(time__gte=target)
    dic = {}
    for i in commitList:
        dic[i.userid] = dic.get(i.userid, 0) + 1
    return sorted(dic.items(), key=lambda x:x[1], reverse=True)


def getCommitsFromAPI(id):
    l = []
    # 현재 event검색, 추후 search api 검색으로 바꿀것
    token = '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'
    headers = {'Authorization': 'token '+token} # token
    url = f'https://api.github.com/users/{id}/events'
    response = requests.get(url, headers=headers).json()
    #print(response)
    for i in response:
        try:
            if i['type']=='PushEvent':
                # id, repository, time, message
                l.append((i['id'], i['repo']['name'], i['created_at'], i['payload']['commits'][0]['message']))
        except:
            continue
    return l

from .models import Commit
def search(request):
    data = []
    if request.method=='POST':
        id = request.POST.get('githubID').split()[0] # 양쪽공백허용
        commitList = getCommitsFromAPI(id)
        
        if commitList: # id검색되면, database refresh
            Commit.objects.filter(userid=id).delete()
            for i in commitList:
                Commit(eventid=i[0], userid=id, repository=i[1], time=i[2][:10], message=i[3]).save()
            data = Commit.objects.filter(userid=id)
    else:
        id = None
    print("id=", id)
    return render(request, 'home/resultpage.html', 
                  {'data': data[:10],
                   'id': id,
                   'rankDay':rankByDate('day'),
                   'rankWeek':rankByDate('week'),
                   'rankMonth':rankByDate('month'),
                   })
    
def showRank(request):
    return render(request, 'home/ranking.html', {})