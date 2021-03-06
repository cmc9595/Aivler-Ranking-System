#from csv import writer
#from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from .models import Question

def index(request): 
    question_list = Question.objects.order_by('-pub_date')
    context = {
        'question_list': question_list
    }
    return render(request, 'qna/question_list.html', context)

def yet(request):
    question_list = Question.objects.filter(qsolve = 0).order_by('-id')
    context = {
        'question_list': question_list
    }
    return render(request, 'qna/question_list1.html', context)

def solve(request):
    question_list = Question.objects.filter(qsolve = 1).order_by('-id')
    context = {
        'question_list': question_list
    }
    return render(request, 'qna/question_list2.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.hits += 1
    question.save()
    context = {
    'question': question
    }
    return render(request, 'qna/question_detail.html', context)

def turnok(request, question_id):
    question = Question.objects.get(pk=question_id)
    question.qsolve = 1
    question.save()
    
    question_list = Question.objects.order_by('-pub_date')
    context = {
        'question_list': question_list
    }
    return render(request, 'qna/question_list.html', context)

from django.utils import timezone
from .forms import QuestionForm

def question_create(request, word):
    if request.method == 'POST':
        form = QuestionForm(request.POST,request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.writer = word
            question.save()
            # if question.file:
            #     name = question.file.name
            #     size = question.file.size
            # return HttpResponse('%s<br>%s' % (name, size))

            return redirect('qna:index')
    else:
        form = QuestionForm()
    context = {'form': form}
    
    return render(request, 'qna/question_form.html', context)

def question_delete(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':
        question.delete()
        return redirect('qna:index')
    return render(request, 'qna/question_delete.html', {'form': question })

from .models import Answer
from .forms import AnswerForm

def answer_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('qna:detail', question_id=question.id)
    else:
        form = AnswerForm()
    context = {'question': question, 'form': form}
    return render(request, 'qna/question_detail.html', context)

def answer_delete(request):
    a = request.POST.get('answer_id')
    target = Answer.objects.get(pk=a)
    target.delete()
    return redirect('/qna/'+ request.POST.get('question_id') )    
