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

def rankByDate(option, params=1):
    today = datetime.now()
    if option=='day':
        target = datetime(year=today.year, month=today.month, day=today.day)
    elif option=='week':
        if today.day <= today.weekday():
            target = datetime(year=today.year, month=today.month, day=1)
        else:
            target = datetime(year=today.year, month=today.month, day=today.day - today.weekday())
    elif option=='month':
        target = datetime(year=today.year, month=today.month, day=1)
        
    commits = Commit.objects.filter(date__gte=str(target))
    dic = {}
    for commit in commits:
        dic[commit.userid] = dic.get(commit.userid, 0) + 1
    res = sorted(dic.items(), key=lambda x:x[1], reverse=True)
    res = [[idx+1, id, cnt]for idx, (id, cnt) in enumerate(res)]
    # 중복 rank
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
    elif params=='dict':
        return dict([(id, idx) for idx, id, cnt in res])

def callAPI(url):
    token = os.environ.get("TOKEN")
    if token is None:
        return None, "No Token", []

    headers = {'Authorization': 'token '+token}
    r = requests.get(url, headers=headers)
    r_status = r.status_code
    if r_status==200:
        return r, r_status, "Success"
    else:
        r = r.json()
        return r, r_status, r['message']
    
def getCommitsFromAPI(id):
    # 현재 event검색, 추후 search api 검색으로 바꿀것
    url = f'https://api.github.com/users/{id}/events?per_page=100&page=1'
    _, status, msg = callAPI(url)

    l = []
    if status==200:
        for page in range(1, 4):
            url = f'https://api.github.com/users/{id}/events?per_page=100&page={page}'
            r, r_status, msg = callAPI(url)

            if r_status==200: # success
                r = r.json()
                for i in r:
                    if i['type']=='PushEvent':
                        l.append((i['id'], i['repo']['name'], i['created_at'], i['payload']['commits'][0]['message']))
            else: # fail
                break

    return status, msg, l


# profileapi
def getProfileFromAPI(id):
    t = []
    url = f'https://api.github.com/users/{id}' # http -> cmc9595; 세미콜론 먹어버리는 버그
    
    response, r_status, msg = callAPI(url)
    if r_status==200:
        response = response.json()
        if response['type']=='User':
            avatar = response['avatar_url']
            html_url = response['html_url']
            name = response['name']
            company = response['company']
            blog = response['blog']
            location = response['location']
            bio = response['bio']
            t = [avatar, html_url, name, company, blog, location, bio]
        elif response['type']=='Organization': 
            return 500, msg, []

    return r_status, msg, t

# update Database with ID
def updateCommit(id):
    status, msg, l = getCommitsFromAPI(id)
    if status==200:
        Commit.objects.filter(userid=id).delete()
        for i in l:
            date, time = i[2].split('T')
            time = time[:-1]
            dt = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')
            dt += timedelta(hours=9) # seoul/Asia = UTC+09:00
            Commit(eventid=i[0], userid=id, repository=i[1], date=dt, message=i[3]).save()
    else:
        pass
    return status, msg

def updateProfile(id):
    status, msg, t = getProfileFromAPI(id)
    if status==200:
        obj, created = GithubUser.objects.get_or_create(
            userid=id, avatar=t[0], html_url=t[1], name=t[2], company=t[3], blog=t[4], location=t[5], bio=t[6])
        if created:
            print("new profile created")
        else:
            print("profile already exists")
    else:
        pass
    return status, msg
        
def search(request):
    if request.method=='GET': # 검색박스
        id = request.GET.get('githubID')
        if id is None:
            id = ''
        else:
            id = id.split() # 양쪽공백 허용
            id = id[0] if id else ''
        
        print("id=", id)
        status, msg = updateCommit(id) # 커밋 DB 업데이트
        print("commit:", status, msg)
        
        status, msg = updateProfile(id) # 프로필 DB 업데이트
        print("profile:", status, msg)
        if status==500:
            return render(request, 'home/error_page.html', {'msg':f'id "{id}" type=Organization, not User'})
        elif status==404:
            return render(request, 'home/error_page.html', {'msg':f'404 Not Found:\nid={id} not found'})


        # 프로필 가져오기
        try:
            profile = GithubUser.objects.get(userid=id)
        except:
            profile = None
            
        data = Commit.objects.filter(userid=id)
        
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
