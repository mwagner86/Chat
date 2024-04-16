# chat/consumers.py

'''code for the asynchronous chat application'''
import json
import logging

from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    """
A class representing a consumer for the asynchronous chat application.

Attributes:
    DATE_FORMAT (str): The format of the date and time used in the chat messages.

Methods:
    __init__(*args, **kwargs): Initializes the ChatConsumer instance.
    connect(): Handles the connection of a user to a chat room.
    username(): Returns the username
    """

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.room_name = "default_room"
        self.logger = logging.getLogger(__name__)

    @property
    def username(self):
        """
        Returns:
            str: The username of the user or 'Anonymous User' if the user is not authenticated.
        """
        user = self.scope['user']
        return user.username if user.is_authenticated else 'Anonymous User'

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
                await self.send_join_message(
                    self.username,
                    datetime.now().strftime(self.DATE_FORMAT)
                    )
            except ConnectionError as e:
                self.logger.error("Failed to connect: %s", str(e))
                await self.close()
        else:
            # Handle unauthenticated user
            self.room_name = "unauthorized"
            self.room_group_name = f"chat_{self.room_name}"

            # Join unauthorized room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
            # Use the username property to get "Anonymous User"
            join_message = f"{self.username} has joined the unauthorized room: Please login to participate in the full chat experience."
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": join_message,
                }
            )


    async def disconnect(self, code):
        """
        Handles the disconnection of a user from a chat room.
        """
        if self.room_group_name:
            user = self.username
            leave_message = f"{user} has left the chat."
            await self.send_leave_message(leave_message)
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            user = self.username  # Use the username property instead of scope["user"].username
            timestamp = datetime.now().strftime(self.DATE_FORMAT)
            formatted_message = f"{user} at {timestamp}: {message}"
            await self.send_chat_message(formatted_message)
        except json.JSONDecodeError as e:
            self.logger.error("Failed to decode JSON: %s", str(e))
            # Send an error message back to the user
            await self.send(text_data=json.dumps({
                'error': 'Invalid message format. Please send a valid JSON.'
            }))

    async def chat_message(self, event):
        """
        Receives a message from the room group.
        """
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    async def send_join_message(self, username, timestamp):
        """
        Sends a join message to the room group.
        Parameters:
        username (str): The username of the user who joined the chat.
        timestamp (str): The timestamp when the user joined the chat.

        Raises:
        Exception: If there is an error while sending the join message.
        """
        try:
            join_message = f"{username} has joined the chat at {timestamp}."
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": join_message,
                }
            )
        except Exception as e:
            self.logger.error("Failed to send join message: %s", str(e))

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
