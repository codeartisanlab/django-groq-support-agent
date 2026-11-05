from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    path('api/chat/', views.chat_endpoint, name='chat_endpoint'),
]