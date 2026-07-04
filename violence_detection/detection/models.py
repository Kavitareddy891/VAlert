from django.db import models
from django.contrib.auth.models import User


class DetectionEvent(models.Model):
    DETECTION_TYPE = [
        ('live', 'Live Camera'),
        ('video', 'Video Upload'),
    ]
    STATUS = [
        ('violence', 'Violence Detected'),
        ('safe', 'No Violence'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    detection_type = models.CharField(max_length=10, choices=DETECTION_TYPE)
    status = models.CharField(max_length=10, choices=STATUS)
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    screenshot = models.ImageField(upload_to='screenshots/', null=True, blank=True)
    video_filename = models.CharField(max_length=255, null=True, blank=True)
    violence_percentage = models.FloatField(null=True, blank=True)
    total_frames = models.IntegerField(null=True, blank=True)
    violence_frames = models.IntegerField(null=True, blank=True)
    telegram_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.detection_type} | {self.status} | {self.confidence:.3f} | {self.timestamp}"


class TelegramSettings(models.Model):
    bot_token = models.CharField(max_length=200)
    chat_id = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    alert_cooldown_seconds = models.IntegerField(default=60)
    last_alert_sent = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Telegram Settings'

    def __str__(self):
        return f"Telegram Bot ({self.chat_id})"


class SystemSettings(models.Model):
    threshold = models.FloatField(default=0.3)
    auto_screenshot = models.BooleanField(default=True)
    telegram_alerts = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'System Settings'

    def __str__(self):
        return "System Settings"
