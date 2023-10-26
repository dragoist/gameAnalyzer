from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.register, name='register'),
    path('teamDataSearch/', views.match_search, name='teamDataSearch'),
]