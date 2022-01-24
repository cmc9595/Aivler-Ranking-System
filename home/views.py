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
    # 사용한 id의 등수 (중복등수 적용)
    rankDay = rankByDate('day')
    rankWeek = rankByDate('week')
    rankMonth = rankByDate('month')
    result1 = []
    blank1 = []
    for key, val in rankDay:
        blank1.append(key)
        r1 = 1
        for key2,val2 in rankDay:
            if val < val2: 
                r1+=1
        result1.append(r1)
    if id in blank1:
        rankD = result1[blank1.index(id)]
    else:
        rankD = '기록이 없습니다.'
    result2 = []
    blank2 = []
    for key, val in rankWeek:
        blank2.append(key)
        r2 = 1
        for key2,val2 in rankWeek:
            if val < val2: 
                r2 += 1
        result2.append(r2)
    if id in blank2:
        rankW = result2[blank2.index(id)]
    else:
        rankW = '기록이 없습니다.'
    result3 = []
    blank3 = []
    for key, val in rankMonth:
        blank3.append(key)
        r3 = 1
        for key2,val2 in rankMonth:
            if val < val2: 
                r3+=1
        result3.append(r3)
    if id in blank3:
        rankM = result3[blank3.index(id)]
    else:
        rankM = '기록이 없습니다.'
        
    
    return render(request, 'home/resultpage.html', 
                  {'data': data[:5], # 최근 10개목록
                   'id': id,
                   'msg':msg,
                   'rankDay':rankByDate('day'),
                   'rankWeek':rankByDate('week'),
                   'rankMonth':rankByDate('month'),
                   'rankD':rankD,
                   'rankW':rankW,
                   'rankM':rankM,
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

from django.core.paginator import Paginator
def paging(request):
    now_page = request.GET.get('page',1)
    rankMonth = rankByDate('month')
    p = Paginator(rankMonth, 2)
    
    info = p.page(now_page)
    
    context = {
        'info':info
    }
    
    return render(request, 'home/resultpage.html', context)

def mainrank(request):
    rankDay = rankByDate('day')
    rankWeek = rankByDate('week')
    rankMonth = rankByDate('month')

    return render(request, 'home/mainpage.html', {
        'rankDay':rankDay,
        'rankWeek':rankWeek,
        'rankMonth':rankMonth,
    })