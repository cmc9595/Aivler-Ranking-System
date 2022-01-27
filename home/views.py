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
def index(request):
    return render(request, 'home/mainpage.html')

def rankByDate(option, params=1): # params 는 (idx, id, count) 원소갯수
    today = datetime.now()
    if option=='day':
        target = datetime(year=today.year, month=today.month, day=today.day)
    elif option=='week':
        target = datetime(year=today.year, month=today.month, day=today.day - today.weekday())
    elif option=='month':
        target = datetime(year=today.year, month=today.month, day=1)
    #print(f"{option}, {target}")
    print("target:", target)
    commits = Commit.objects.filter(date__gte=str(target))
    for i in commits:
        if i.userid=='jhg2957':
            print(i.eventid, i.userid, i.date, i.message)
    print("len:", len(commits))
    dic = {}
    for commit in commits:
        dic[commit.userid] = dic.get(commit.userid, 0) + 1
    print(dic)
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


def getCommitsFromAPI(id):
    # 현재 event검색, 추후 search api 검색으로 바꿀것
    token = os.environ.get("TOKEN")
    if token is None:
        return "no token"
    headers = {'Authorization': 'token '+token} # token
    url = f'https://api.github.com/users/{id}/events'
    response = requests.get(url, headers=headers).json()
    try:
        if response['message']=='Not Found':
            return 'id not found'
        if response['message']=='Bad credentials':
            return 'token - bad credential'
    except:
        pass
    
    l = []
    page = 0
    while True:
        page += 1
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
            Commit(eventid=int(i[0]), userid=id, repository=i[1], date=dt, message=i[3]).save()
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
        #sidebar = request.GET.get('sidebar')
        if id is None:
            id = ''
        else:
            id = id.split() # 양쪽공백 허용
            if id:
                id = id[0]
            else:
                id = ''
        
        msg = updateCommit(id) # 커밋 DB 업데이트
        # 커밋정보가 없어도, 프로필이 있으면 출력해준다!!
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
        # profile 가져오는부분 
        # profileList = getProfileFromAPI(id)
        # if profileList=='no token':
        #     msg = 'no token'
        # elif profileList==[]:
        #     msg = 'id가 틀리거나 토큰만료'
        #     avatar = ""
        #     html_url = ""
        #     company = ""
        #     blog = ""
        #     location = ""
        #     bio = ""
        # else :
        #     avatar = profileList[0]
        #     html_url = profileList[1]
        #     company = profileList[2]
        #     blog = profileList[3]
        #     location = profileList[4]
        #     bio = profileList[5]    
        
        print("id=", id)
        # 사용한 id의 등수 (중복등수 적용)
        dayIDs = rankByDate('day', 1)
        weekIDs = rankByDate('week', 1)
        monthIDs = rankByDate('month', 1)
        
        # 이용자수
        dayuser = len(dayIDs)
        weekuser = len(weekIDs)
        monthuser = len(monthIDs)
        
        
        dayRank = rankByDate('day',4)
        weekRank = rankByDate('week',4)
        monthRank = rankByDate('month',4)
        dayRank_a = dayIDs.index(id) if id in dayIDs else '-'
        weekRank_b = weekIDs.index(id) if id in weekIDs else '-'
        monthRank_c = monthIDs.index(id) if id in monthIDs else '-'
        dayRank = dayRank[dayRank_a] if dayRank_a != '-' else '-' 
        weekRank = weekRank[weekRank_b]
        monthRank = monthRank[monthRank_c]
    
        return render(request, 'home/profile.html', 
                    {'data': data[:5], # 최근 5개목록
                    'id': id,
                    #'sidebar':sidebar,
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

def mainrank(request):
    dayList = [(idx, id, cnt, GithubUser.objects.get(userid=id)) for idx, id, cnt in rankByDate('day', 3)]
    weekList = [(idx, id, cnt, GithubUser.objects.get(userid=id)) for idx, id, cnt in rankByDate('week', 3)]
    monthList = [(idx, id, cnt, GithubUser.objects.get(userid=id)) for idx, id, cnt in rankByDate('month', 3)]

    unsolved_list = Question.objects.filter(qsolve = 0).order_by('-id')
    unsolved_len = len(unsolved_list)
    if unsolved_len > 4 :
        unsolved_len = 4
    unsolved_list = Question.objects.filter(qsolve = 0).order_by('-id')[:unsolved_len]

    # dayRank = rankByDate('day', 3)
    # weekRank = rankByDate('week', 3)
    # monthRank = rankByDate('month', 3)
    return render(request, 'home/mainpage.html', {
        # 'rankD':dayRank,
        # 'rankW':weekRank,
        # 'rankM':monthRank,
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
        new_list.append([rank, id, cnt, GithubUser.objects.get(userid=id)])
        
        # a = getProfileFromAPI(key)
        # avatar = a[0]
        # git_url = a[1]
        # location = (a[-2])
        # bio = (a[-1])
        # new = (idx,key,val,avatar,location,bio)
        # new_list.append(new)    
        
    return render(request, 'home/resultpage.html',
                  {'option': option,
                   #'returnList': returnList,
                    'new_list':new_list,
                   })