from django.urls import path
from . import views

app_name = 'ask'

urlpatterns = [
    path('', views.ask, name= 'ask'),
]