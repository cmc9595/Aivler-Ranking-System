from django.shortcuts import render
from django.http import HttpResponse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from django.utils import timezone

load_dotenv()
# Create your views here.
def index(request):
    return render(request, 'home/mainpage.html', {})

def rankByDate(option):
    today = timezone.now()
    #print("현재시간", timezone.now())
    if option=='day':
        diff = timedelta(hours=today.hour, minutes=today.minute, seconds=today.second)
    elif option=='week':
        diff = timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute, seconds=today.second)
    elif option=='month':
        diff = timedelta(days=today.day-1, hours=today.hour, minutes=today.minute, seconds=today.second)
    target = str(today - diff)
    #print(f"{option}, {target}")
    commitList = Commit.objects.filter(date__gte=target)
    dic = {}
    for i in commitList:
        dic[i.userid] = dic.get(i.userid, 0) + 1
    return sorted(dic.items(), key=lambda x:x[1], reverse=True)


def getCommitsFromAPI(id):
    l = []
    # 현재 event검색, 추후 search api 검색으로 바꿀것
    token = os.environ.get("TOKEN")
    if token is None:
        return "no token"
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
    msg = ''
    if request.method=='POST': # 검색박스
        id = request.POST.get('githubID').split() # 양쪽공백허용
        if id:
            id = id[0]
        else:
            id = ''
            
        commitList=getCommitsFromAPI(id)
        if commitList=='no token':
            msg = 'no token'
        elif commitList==[]:
            msg = 'id가 틀리거나 토큰만료'
        else:
            # id검색되면, database refresh
            Commit.objects.filter(userid=id).delete()
            for i in commitList:
                date, time = i[2].split('T')
                time = time[:-1]
                dt = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')
                dt += timedelta(hours=9) # seoul/Asia = UTC+09:00
                Commit(eventid=i[0], userid=id, repository=i[1], date=dt, message=i[3]).save()
            data = Commit.objects.filter(userid=id)
            
    else: # 사이드바 '전체랭킹'으로 접속
        id = None
    print("id=", id)
    return render(request, 'home/resultpage.html', 
                  {'data': data[:10], # 최근 10개목록
                   'id': id,
                   'msg':msg,
                   'rankDay':rankByDate('day'),
                   'rankWeek':rankByDate('week'),
                   'rankMonth':rankByDate('month'),
                   })
    
def showRank(request):
    return render(request, 'home/ranking.html', {})

def commitmsg(request):
    num = int(request.GET.get('num'))
    #print("num=", num)
        
    obj = Commit.objects.order_by('-date')[num] # date 최근별 정렬
    #print(commitMsg)
    result = f'{obj.message}<br>{obj.userid}<br>{obj.date}'
    return HttpResponse(result)
