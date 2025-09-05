from django.urls import path
from . import views, views_auth

urlpatterns = [
    path('', views.upload_and_generate, name='upload'),


    # login
    path('login/', views_auth.user_login, name='login'),
    path('register/', views_auth.user_register, name='register'),
    path('logout/', views_auth.user_logout, name='logout'),
    path('my-videos/', views.my_videos, name='my_videos'),
    path('memorial/create/', views.create_memorial, name='create_memorial'),
    path('memorial/<uuid:memorial_id>/', views.memorial_detail, name='memorial_detail'),

]
