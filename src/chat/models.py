# chat/models.py
from django.db import models
from django.contrib.auth import get_user_model


class ChatMessage(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.room_name} at {self.timestamp}"

class DirectMessage(models.Model):
    sender = models.ForeignKey(get_user_model(), related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(get_user_model(), related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username} at {self.timestamp}"