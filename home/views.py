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
    headers = {'Authorization': 'token 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'} # token
    url = f'https://api.github.com/users/{id}/events'
    response = requests.get(url, headers=headers).json()
    #print(response) 잘 안될땐 여기 보셈
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
        id = request.POST.get('githubID')
        print(id)
        commitList = getCommitsFromAPI(id)
        
        if commitList: # id검색되면, database refresh
            Commit.objects.filter(userid=id).delete()
            for i in commitList:
                Commit(eventid=i[0], userid=id, repository=i[1], time=i[2][:10], message=i[3]).save()
            data = Commit.objects.filter(userid=id)
    elif request.method=='GET':
        id = request.GET.get('githubID')
    else:
        id = '123'
        data = None
        
    return render(request, 'home/resultpage.html', 
                  {'data': data,
                   'id': id,
                   'rankDay':rankByDate('day'),
                   'rankWeek':rankByDate('week'),
                   'rankMonth':rankByDate('month'),
                   })
    
def showRank(request):
    return render(request, 'home/ranking.html', {})