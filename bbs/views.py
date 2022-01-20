import imp
from django.shortcuts import render

from .models import Post

def free(request):
    postlist = Post.objects.all()
    return render(request, 'bbs/free.html', {'postlist':postlist})

def posting(request, pk):
    post = Post.objects.get(pk=pk)
    return render(request, 'bbs/posting.html', {'post':post})