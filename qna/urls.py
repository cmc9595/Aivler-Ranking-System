from django.urls import path
from . import views

app_name = 'qna'
urlpatterns = [
    path('', views.index, name = 'index'),  # 질문리스트
    path('yet/', views.yet, name= 'yet'),   # 미해결 질문 리스트
    path('solve/', views.solve, name = 'solve'), # 해결된 질문 리스트

    path('<int:question_id>/', views.detail, name= 'detail'), # 상세질문
    path('<int:question_id>/ok/', views.turnok, name= 'ok'), # 질문 -> 해결완료 

    path('question/create/<word>/', views.question_create, name='question_create'), # 새 질문 작성
    path('<int:question_id>/delete/', views.question_delete, name='question_delete'), # 질문 삭제

    path('answer/create/<int:question_id>/', views.answer_create,name='answer_create'), # 댓글 작성
    path('answer/delete/', views.answer_delete, name='answer_delete'), # 댓글 삭제
    
]
