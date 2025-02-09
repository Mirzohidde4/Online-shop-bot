from django.shortcuts import render, redirect

# Create your views here.
def HomeView(request):
    return redirect('admin/')
    