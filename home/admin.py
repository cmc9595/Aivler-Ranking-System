from atexit import register
from django.contrib import admin
from .models import Commit
# Register your models here.

admin.site.register(Commit)