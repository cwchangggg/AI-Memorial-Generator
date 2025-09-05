from django.db import models
from django.contrib.auth.models import User
import uuid

from django.utils import timezone



class GeneratedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    audio_filename = models.CharField(max_length=255)
    video_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.video_path.split('/')[-1]

class MemorialPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    biography = models.TextField(blank=True)
    cover_photo = models.ImageField(upload_to='memorial_photos/', blank=True, null=True)
    memorial_video = models.ForeignKey(GeneratedVideo, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class FlowerOffering(models.Model):
    memorial_page = models.ForeignKey(MemorialPage, on_delete=models.CASCADE, related_name='flowers')
    name = models.CharField(max_length=30)  # visitor's name 
    flower_type = models.CharField(max_length=20)  # flower type
    message = models.TextField(blank=True)  # comment
    created_at = models.DateTimeField(default=timezone.now)
    emoji= '🌼'

    def __str__(self):
        return f"{self.name} 獻上 {self.flower_type}"