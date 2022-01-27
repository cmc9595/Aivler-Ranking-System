from csv import writer
from django.db import models

class Question(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField()
    hits = models.IntegerField(default='0')
    file = models.FileField(upload_to='%Y/%m/%d',blank=True)
    qsolve = models.IntegerField(default='0')
    writer =  models.CharField(max_length=150, blank=True)
    code_edit = models.TextField(blank=True)

    def __str__(self):
        return self.subject+" / "
    def summary(self):
        return self.content[:80]
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    def __str__(self):
        return self.question
