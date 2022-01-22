from django.urls import path
from . import views

app_name = 'bbs'
urlpatterns = [
    path('', views.free, name= 'free'),
    path('<int:pk>/',views.posting, name="posting"),
    path('new_post/', views.new_post),
    path('<int:pk>/remove/', views.remove_post),
]