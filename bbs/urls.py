from django.urls import path
from . import views

urlpatterns = [
    path('', views.free),
    path('<int:pk>/',views.posting, name="posting"),
]