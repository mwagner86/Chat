# chat/admin.py

from django.contrib import admin
from .models import ChatMessage, DirectMessage

admin.site.register(ChatMessage)
admin.site.register(DirectMessage)