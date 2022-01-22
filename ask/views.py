import imp
from django.shortcuts import render
from django.http import HttpResponse

def ask(request):
    return HttpResponse('<u>Hello</u>')
