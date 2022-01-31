import sys
sys.path.append('/home/ubuntu/Aivler-Ranking-System/')

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from datetime import datetime
from home.views import updateAll, updateCommit
from home.models import GithubUser, Commit

def hello_every_minute():
    print('======================')
    print(f'Job executed at {datetime.now()}')

def updateUserInfo():
    print('-------------')
    print(f'Github Commit Info Updated at : {datetime.now()}')

    users = GithubUser.objects.all()
    for user in users:
        msg = updateCommit(user.userid)
        print(msg, user.userid, datetime.now())

if __name__=='__main__':
    updateUserInfo()
