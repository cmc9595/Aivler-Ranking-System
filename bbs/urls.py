from django.urls import path
from . import views

app_name = 'bbs'
urlpatterns = [
    path('', views.free, name= 'free'),
    path('<int:post_id>/',views.posting, name="posting"),
    path('new_post/', views.new_post),
    path('<int:post_id>/remove/', views.remove_post),

    path('comment/create/<int:post_id>/', views.comment_create,name='comment_create'), # 댓글 작성
]