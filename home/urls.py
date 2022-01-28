from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.mainrank, name='mainrank'),
    
    path('search/', views.search, name='search'),
    path('home/', views.mainrank, name='mainrank'),
    path('commitmsg/', views.commitmsg, name='commitmsg'),
    path('ranking/', views.ranking, name='ranking'),
    path('updateAll/', views.updateAll, name='updateAll'),
    
]
