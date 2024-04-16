# chat/consumers.py

'''code for the asynchronous chat application'''
import json
import logging

from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
# TIME_ZONE = 'Europe/Berlin' in settings.py file.
# USE_TZ = True in settings.py file.
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
        """
        Handles the connection of a user to a chat room in the asynchronous chat application.
        """
        user = self.scope["user"]
        if user.is_authenticated:
            try:
                self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
                self.room_group_name = f"chat_{self.room_name}"

                # Join room group
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)

                await self.accept()
                # Send message to room group
                await self.send_join_message(user.username)
            except ConnectionError as e:
                logging.error("Failed to connect: %s", str(e))
                await self.close()
        else:
            await self.close()

    async def disconnect(self, code):
        """
        Handles the disconnection of a user from a chat room.
        """
        if self.room_group_name:
            user = self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous User"
            leave_message = f"{user} has left the chat."
            await self.send_leave_message(leave_message)
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receives a message from a WebSocket.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope["user"].username
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{user} at {timestamp}: {message}"
        await self.send_chat_message(formatted_message)

    async def chat_message(self, event):
        """
        Receives a message from the room group.
        """
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    async def send_join_message(self, username):
        """
        Sends a join message to the room group.
        """
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": f"{username} has joined the chat.",
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    async def send_leave_message(self, message):
        """
        Sends a leave message to the room group.
        """
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def send_chat_message(self, message):
        """
        Sends a chat message to the room group.
        """
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )
