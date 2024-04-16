# chat/consumers.py

'''code for the asynchronous chat application'''
import json
import logging

from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

# Debugging: remove later
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None

    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            try:
                self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
                self.room_group_name = f"chat_{self.room_name}"

                # Join room group
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)

                await self.accept()
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": f"{user.username} has joined the chat.",
                        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
            except ConnectionError as e:
                logging.error("Failed to connect: %s", str(e))
                await self.close()
        else:
            await self.close()

    async def disconnect(self, code):
        if self.room_group_name:
            user = self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous User"
            leave_message = f"{user} has left the chat."
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": leave_message}
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope["user"].username
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{user} at {timestamp}: {message}"
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": formatted_message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
