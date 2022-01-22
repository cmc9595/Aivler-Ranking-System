import imp
from django.shortcuts import render, redirect

from .models import Post

def ask(request):
    postlist = Post.objects.all()
    return render(request, 'ask/question.html', {'postlist':postlist})

def posting(request, pk):
    post = Post.objects.get(pk=pk)
    return render(request, 'ask/posting.html', {'post':post})

def new_post(request):
    if request.method == 'POST':
        new_article=Post.objects.create(
            question=request.POST['question'],
            contents=request.POST['contents'],
        )
        new_article.save()
        return redirect('/ask/')
    return render(request, 'ask/new_post.html')

def remove_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('/ask/')
    return render(request, 'ask/remove_post.html', {'Post': post})