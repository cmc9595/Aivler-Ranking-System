from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    
    path('search/', views.search, name='search'),
    path('showrank/', views.showRank, name='showRank'),
    path('home/', views.mainrank),
    path('commitmsg/', views.commitmsg, name='commitmsg'),
    path('ranking/', views.ranking, name='ranking'),
]