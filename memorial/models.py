from django.db import models
from django.contrib.auth.models import User

class GeneratedVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    audio_filename = models.CharField(max_length=255)
    video_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.video_path.split('/')[-1]
