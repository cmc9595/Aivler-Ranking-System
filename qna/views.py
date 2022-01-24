from django.shortcuts import render
from django.http import HttpResponse
from .models import Question

from django.shortcuts import get_object_or_404

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

def detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    context = {
    'question': question
    }
    return render(request, 'qna/question_detail.html', context)

from django.utils import timezone
# from .models import Answer
from django.shortcuts import redirect

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


from .forms import QuestionForm
def question_create(request):
    form = QuestionForm()
    return render(request, 'qna/question_form.html', {'form': form})

def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()
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
