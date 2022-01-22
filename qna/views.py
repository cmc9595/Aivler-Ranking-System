from django.shortcuts import render
from django.http import HttpResponse
from .models import Question

from django.shortcuts import get_object_or_404

def detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    context = {
    'question': question
    }
    return render(request, 'qna/question_detail.html', context)

def index(request):
    question_list = Question.objects.order_by('-pub_date')
    context = {
        'question_list': question_list
    }
    return render(request, 'qna/question_list.html', context)

def detail(request, question_id):
    question = Question.objects.get(id=question_id)
    context = {
    'question': question
    }
    return render(request, 'qna/question_detail.html', context)

from django.utils import timezone
# from .models import Answer
from django.shortcuts import redirect

def answer_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.answer_set.create(
        content=request.POST.get('content'), create_date=timezone.now())
    # answer = Answer(
    # question=question, content=request.POST.get('content'),
    # create_date=timezone.now())
    # answer.save()
    return redirect('qna:detail', question_id=question.id)

def question_create(request):

    return render(request, 'qna/question_form.html')

