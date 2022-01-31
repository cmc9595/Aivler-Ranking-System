from django.shortcuts import render
from django.http import HttpResponse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Commit, GithubUser
from qna.models import Question

load_dotenv()

def rankByDate(option, params=1): # params 는 (idx, id, count) 원소갯수
    today = datetime.now()
    if option=='day':
        target = datetime(year=today.year, month=today.month, day=today.day)
    elif option=='week':
        if today.day <= today.weekday():
            target = datetime(year=today.year, month=today.month, day=today.day)
        else:
            target = datetime(year=today.year, month=today.month, day=today.day - today.weekday())
    elif option=='month':
        target = datetime(year=today.year, month=today.month, day=1)
        
    commits = Commit.objects.filter(date__gte=str(target))
    # print("len:", len(commits))
    dic = {}
    for commit in commits:
        dic[commit.userid] = dic.get(commit.userid, 0) + 1
    res = sorted(dic.items(), key=lambda x:x[1], reverse=True)
    res = [[idx+1, id, cnt]for idx, (id, cnt) in enumerate(res)]
    # 중복 rank 적용
    for i in range(len(res)-1):
        if res[i][2]==res[i+1][2]:
            res[i+1][0] = res[i][0]
    
    if params==1:
        return [(id) for idx, id, cnt in res]
    elif params==2:
        return [(id, cnt) for idx, id, cnt in res]
    elif params==3:
        return res
    elif params==4:
        return [(idx) for idx, id, cnt in res]
    # dictation form
    elif params=='dict':
        return dict([(id, idx) for idx, id, cnt in res])

def getCommitsFromAPI(id):
    # 현재 event검색, 추후 search api 검색으로 바꿀것
    token = os.environ.get("TOKEN")
    if token is None:
        return "no token"
    headers = {'Authorization': 'token '+token} # token
    l = []
    for page in range(1, 4): # 4page까지
        url = f'https://api.github.com/users/{id}/events?per_page=100&page={page}'
        response = requests.get(url, headers=headers).json()
        if response == []: # last page break
            break
        for i in response:
            try:
                if i['type']=='PushEvent':
                    # id, repository, date, message
                    l.append((i['id'], i['repo']['name'], i['created_at'], i['payload']['commits'][0]['message']))
            except:
                continue
    print("len:", len(l))
    print("page:", page)
    return l
# profileapi
def getProfileFromAPI(id):
    t = []
    token = os.environ.get("TOKEN")
    if token is None:
        return "no token"
    headers = {'Authorization': 'token '+token}
    url = f'http://api.github.com/users/{id}'
    
    response = requests.get(url, headers=headers).json()
    try :
        if response['type']=='User':
            avatar = response['avatar_url']
            html_url = response['html_url']
            name = response['name']
            company = response['company']
            blog = response['blog']
            location = response['location']
            bio = response['bio']
            t = [avatar, html_url, name, company, blog, location, bio]
    except:
        t = []         
    return t

# update Database with ID
def updateCommit(id):
    commits = getCommitsFromAPI(id)
    if commits == "no token":
        return "no token"
    elif commits == 'id not found':
        return 'id not found'
    elif commits == 'token - bad credential':
        return 'token - bad credential'
    else:
        Commit.objects.filter(userid=id).delete()
        for i in commits:
            date, time = i[2].split('T')
            time = time[:-1]
            dt = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')
            dt += timedelta(hours=9) # seoul/Asia = UTC+09:00
            Commit(eventid=i[0], userid=id, repository=i[1], date=dt, message=i[3]).save()
        return ''

def updateProfile(id):
    profile = getProfileFromAPI(id)
    if profile == "no token":
        return "no token"
    elif profile == []:
        return "wrong id or token"
    else:
        obj, created = GithubUser.objects.get_or_create(
            userid=id,
            avatar=profile[0],
            html_url=profile[1],
            name=profile[2],
            company=profile[3],
            blog=profile[4],
            location=profile[5],
            bio=profile[6])
        if created:
            print("new profile created")
        else:
            print("profile already exists")
        return ''
        
def search(request):
    if request.method=='GET': # 검색박스
        id = request.GET.get('githubID')
        if id is None:
            id = ''
        else:
            id = id.split() # 양쪽공백 허용
            id = id[0] if id else ''
        
        msg = updateCommit(id) # 커밋 DB 업데이트
        # if msg=='no token' or msg=='wrong id or token':
        #     return render(request, 'home/error_page.html', {'msg':msg})
        
        msg = updateProfile(id) # 프로필 DB 업데이트
        if msg in ['no token' in 'wrong id or token']:
            return render(request, 'home/error_page.html', {'msg':msg})
        
        # 프로필 가져오기
        try:
            profile = GithubUser.objects.get(userid=id)
        except:
            profile = None
            
        data = Commit.objects.filter(userid=id)
        
        print("id=", id)
        dayRank = dayDict[id] if id in (dayDict:=rankByDate('day', 'dict')).keys() else '-'
        weekRank = weekDict[id] if id in (weekDict:=rankByDate('week', 'dict')).keys() else '-'
        monthRank = monthDict[id] if id in (monthDict:=rankByDate('month', 'dict')).keys() else '-'
        # 이용자수
        dayuser = len(dayDict)
        weekuser = len(weekDict)
        monthuser = len(monthDict)
    
        return render(request, 'home/profile.html', 
                    {'data': data[:5], # 최근 5개목록
                    'id': id,
                    'rankD':dayRank,
                    'rankW':weekRank,
                    'rankM':monthRank,
                    'profile':profile,
                    'dayuser':dayuser,
                    'weekuser':weekuser,
                    'monthuser':monthuser})

def commitmsg(request):
    num = int(request.GET.get('num'))
    try:
        obj = Commit.objects.order_by('-date')[num] # date 최근별 정렬
        result = f'{obj.message}<br>{obj.userid}<br>{obj.date}'
    except:
        result = ''
    return HttpResponse(result)

# update all GithubUsers
def updateAll(request):
    users = GithubUser.objects.all()
    for user in users:
        msg = updateCommit(user.userid)
        print(msg, user.userid, datetime.now())
    print("updated all")
    return HttpResponse('Done')   

def mainrank(request):
    dayList = [(idx, id, cnt, GithubUser.objects.get(userid=id)) for idx, id, cnt in rankByDate('day', 3)]
    weekList = [(idx, id, cnt, GithubUser.objects.get(userid=id)) for idx, id, cnt in rankByDate('week', 3)]
    monthList = [(idx, id, cnt, GithubUser.objects.get(userid=id)) for idx, id, cnt in rankByDate('month', 3)]

    unsolved_list = Question.objects.filter(qsolve = 0).order_by('-id')
    unsolved_len = len(unsolved_list)
    if unsolved_len > 4 :
        unsolved_len = 4
    unsolved_list = Question.objects.filter(qsolve = 0).order_by('-id')[:unsolved_len]

    return render(request, 'home/mainpage.html', {
        'unsolved_list': unsolved_list,
        'allList':[dayList,weekList,monthList],
    })
    
def ranking(request): # 사이드바, 버튼
    option = request.GET.get('option', 'daily')
    if option == 'daily':
        returnList = rankByDate('day', 3)
    elif option=='weekly':
        returnList = rankByDate('week', 3)
    elif option=='monthly':
        returnList = rankByDate('month', 3)
    # 렉이 많이 걸리는 부분 (코드 수정 ... 검토)
    new_list = []
    for rank, id, cnt in returnList:
        try:
            obj=GithubUser.objects.get(userid=id)
        except:
            updateProfile(id) 
        new_list.append([rank, id, cnt, GithubUser.objects.get(userid=id)])
        
    return render(request, 'home/resultpage.html',
                  {'option': option,
                    'new_list':new_list,
                   })
