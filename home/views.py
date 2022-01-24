from django.shortcuts import render
from django.http import HttpResponse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from django.utils import timezone
from django.core.paginator import Paginator

load_dotenv()
# Create your views here.
def index(request):
    return render(request, 'home/mainpage.html', {})

def rankByDate(option, params): # params 0:(id, cnt), 1:(id)
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
    result = sorted(dic.items(), key=lambda x:x[1], reverse=True)
    result = [(idx+1, i[0], i[1]) for idx, i in enumerate(result)]
    print(result)
    if params==0:
        return result
    elif params==1:
        return [key for idx, key, val in result] # id만 return


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
        now_page1 = request.GET.get('page1', 1) # 'page' 안넘어오면 1 반환.
        now_page2 = request.GET.get('page2', 1)
        now_page3 = request.GET.get('page3', 1)
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
        now_page1 = request.GET.get('page1', 1)
        now_page2 = request.GET.get('page2', 1)
        now_page3 = request.GET.get('page3', 1)
        
    print("id=", id)
    # 사용한 id의 등수 (중복등수 적용)
    dayIDs = rankByDate('day', 1)
    weekIDs = rankByDate('week', 1)
    monthIDs = rankByDate('month', 1)
    
    dayRank = dayIDs.index(id)+1 if id in dayIDs else None
    weekRank = weekIDs.index(id)+1 if id in weekIDs else None
    monthRank = monthIDs.index(id)+1 if id in monthIDs else None
   
    now_pages = [now_page1, now_page2, now_page3]
    rankLists = [rankByDate('day', 0), rankByDate('week', 0), rankByDate('month', 0)]
    pageSize = 5
    res = []
    for now_page, rankList in zip(now_pages, rankLists):
        p = Paginator(rankList, pageSize)
    
        now_page = int(now_page)
        start = (now_page - 1)//pageSize*pageSize + 1
        end = start + pageSize
        if end > p.num_pages:
            end = p.num_pages
 
        res.append((p.page(now_page), range(start, end+1)))
        
    return render(request, 'home/resultpage.html', 
                  {'data': data[:5], # 최근 10개목록
                   'id': id,
                   'msg':msg,
                   'rankDay': res[0][0],
                   'rankWeek':res[1][0],
                   'rankMonth':res[2][0],
                   'rankD':dayRank,
                   'rankW':weekRank,
                   'rankM':monthRank,
                   'page_range1' : res[0][1],
                   'page_range2' : res[1][1],
                   'page_range3' : res[2][1],
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