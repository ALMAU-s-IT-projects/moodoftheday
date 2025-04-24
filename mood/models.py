from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

class Emotion(models.Model):
    CATEGORY_CHOICES = [
        ('positive', 'Позитивные'),
        ('neutral', 'Нейтральные'),
        ('negative', 'Негативные'),
    ]

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, help_text="Цвет фона (#FFE066)")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='neutral')

    def __str__(self):
        return self.name

class ImageOption(models.Model):
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')

class Track(models.Model):
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE, related_name='tracks')
    audio = models.FileField(upload_to='tracks/')

class Quote(models.Model):
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE, related_name='quotes')
    text = models.TextField()

class MoodEntry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)