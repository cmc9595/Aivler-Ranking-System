from django.db import models

# Create your models here.


class GithubUser(models.Model):
    userid = models.CharField(max_length=50)
    avatar = models.CharField(max_length=200, null=True)
    html_url = models.CharField(max_length=200)
    name = models.CharField(max_length=200, null=True)
    company = models.CharField(max_length=100, null=True)
    blog = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    bio = models.CharField(max_length=100, null=True)
    
class Commit(models.Model):
    eventid = models.IntegerField()
    userid = models.CharField(max_length=50)
    repository = models.CharField(max_length=100)
    date = models.DateTimeField()
    message = models.CharField(max_length=1000)
    