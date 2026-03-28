from django.http import HttpResponse
from django.shortcuts import render

# Default index view


def index(request):
    return HttpResponse("Hello from the stores app!")

# Example additional view


def health_check(request):
    return HttpResponse("Stores app is running.")
