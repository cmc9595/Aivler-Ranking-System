from django.shortcuts import render
from django.http import HttpResponse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from django.utils import timezone


def index(request):
  return render(request, 'guest_book/index.html')