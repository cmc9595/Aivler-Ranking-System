from django.db import models

# Create your models here.
class Post(models.Model):
    question = models.CharField(max_length=50)
    contents = models.TextField()

class Answer(models.Model):
    answer = models.TextField()