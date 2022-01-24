from django import forms

from .models import Post
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['postname', 'contents']
        
        labels = {
            'postname': '제목',
            'contents': '내용',
        }

from .models import Comment
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '답변내용',
        }