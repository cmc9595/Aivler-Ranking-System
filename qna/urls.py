from django.urls import path
from . import views

app_name = 'qna'
urlpatterns = [
    path('', views.index, name = 'index'),  #질문리스트
    path('<int:question_id>/', views.detail, name= 'detail'), # 상세질문
    path('<int:question_id>/ok/', views.ok, name= 'ok'), # 상세질문
    path('solve/', views.solve, name = 'solve'),
    path('answer/create/<int:question_id>/', views.answer_create,name='answer_create'), # 댓글 작성
    path('question/create/', views.question_create, name='question_create'),
    path('question/answer_remove/', views.answer_remove, name='answer_remove'),
    path('question/create/', views.question_create, name='question_create'),  # 질문 새로 작성
    path('<int:question_id>/delete/', views.question_delete, name='question_delete'), 
]
