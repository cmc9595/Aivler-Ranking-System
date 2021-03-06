from django import forms

from .models import Question
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'content', 'file','code_edit']
        
        labels = {
            'subject': '제목',
            'content': '내용',
        }

from .models import Answer
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '답변내용',
        }