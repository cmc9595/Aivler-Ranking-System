from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    
    path('search/', views.search, name='search'),
    path('home/', views.mainrank, name='mainrank'),
    path('commitmsg/', views.commitmsg, name='commitmsg'),
    path('ranking/', views.ranking, name='ranking'),
]