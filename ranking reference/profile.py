import requests
import json
# repository 
id = 'dhy02094'
response = requests.get(f'https://api.github.com/users/{id}/repos').json()
repos = [i['html_url'].split('/')[-1] for i in response]

for repo in repos:
    response = requests.get(f'https://api.github.com/repos/{id}/{repo}/commits').json()
    print(f'<{repo}>')
    for i in response:
        print(i['commit']['committer']['date'], i['commit']['message'])
    print()

#profile
response2 = requests.get(f'https://api.github.com/users/{id}').json()
key = [0,3,6,18,24]  #id, image, git_url,name, bio
for i in key:
    print(list(response2.values())[i])