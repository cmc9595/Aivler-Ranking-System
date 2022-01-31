from datetime import datetime
from .views import updateAll

def hello_every_minute():
    print('======================')
    print(f'Job executed at {datetime.now()}')

def updateUserInfo():
    print('-------------')
    print(f'Github Commit Info Updated at : {datetime.now()}')
    updateAll()
