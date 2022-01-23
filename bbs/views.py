import imp
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from .models import Post

def free(request):
    postlist = Post.objects.all()
    page = request.GET.get('page', '1')
    # 한 페이지에 출력할 갯수
    paginator = Paginator(postlist, 3)
    page_obj = paginator.get_page(page)

    return render(request, 'bbs/free.html', {'postlist':page_obj})

def posting(request, pk):
    post = Post.objects.get(pk=pk)
    return render(request, 'bbs/posting.html', {'post':post})

def new_post(request):
    if request.method == 'POST' and request.POST['postname'] != '':
        new_article=Post.objects.create(
            postname=request.POST['postname'],
            contents=request.POST['contents'],
        )
        new_article.save()
        return redirect('/free/')
    elif request.method == 'POST' and request.POST['postname'] == '' :
        context = {'written' : request.POST['contents']}
        return render(request, 'bbs/new_post.html', context)
    return render(request, 'bbs/new_post.html')

def remove_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('/free/')
    return render(request, 'bbs/remove_post.html', {'Post': post})