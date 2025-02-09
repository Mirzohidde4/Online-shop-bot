from django.contrib import admin
from django.urls import path
from main.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView, name='home'),
]
