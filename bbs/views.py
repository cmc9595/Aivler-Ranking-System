import imp
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import Post

def free(request):
    postlist = Post.objects.all()
    page = request.GET.get('page', '1')
    # 한 페이지에 출력할 갯수
    paginator = Paginator(postlist, 3)
    page_obj = paginator.get_page(page)

    return render(request, 'bbs/free.html', {'postlist':page_obj})

def posting(request, post_id):
    post = Post.objects.get(id=post_id)
    context = {
        'post': post
    }
    return render(request, 'bbs/posting.html', context)

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

def remove_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('/free/')
    return render(request, 'bbs/remove_post.html', {'Post': post})


from django.utils import timezone
from .models import Comment
from django.shortcuts import redirect

from .forms import CommentForm

def comment_create(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.create_date = timezone.now()
            comment.post = post
            comment.save()
            return redirect('bbs:posting', post_id=post.id)
    else:
        form = CommentForm()
    context = {'post': post, 'form': form}
    return render(request, 'bbs/posting.html', context)

def comment_delete(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == "GET":
        comment.delete()
        return redirect('bbs:posting', post_id=post.id)
    context = {'post': post, 'form': Comment.objects.all()}
    return render(request, 'bbs/posting.html', context)  


from django.shortcuts import render
from django.http import HttpResponse
def upload(request):
    if request.method == 'POST':
        upload_files = request.FILES.getlist('file')
        
        result = ''
        for upload_file in upload_files:
            name = upload_file.name
            size = upload_file.size
            with open(name, 'wb') as file:
                for chunk in upload_file.chunks():
                    file.write(chunk)
            result += '%s<br>%s<hr>' % (name, size)
        return HttpResponse(result)
    return render(request, 'bbs/upload.html')