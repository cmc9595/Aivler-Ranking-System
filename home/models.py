from django.db import models

# Create your models here.

class Commit(models.Model):
    eventid = models.IntegerField()
    userid = models.CharField(max_length=50)
    repository = models.CharField(max_length=100)
    date = models.DateTimeField()
    message = models.CharField(max_length=1000)
    