from django.urls import path
from . import views, views_auth

urlpatterns = [
    path('', views.upload_and_generate, name='upload'),


    # login
    path('login/', views_auth.user_login, name='login'),
    path('register/', views_auth.user_register, name='register'),
    path('logout/', views_auth.user_logout, name='logout'),
    path('my-videos/', views.my_videos, name='my_videos'),

]
