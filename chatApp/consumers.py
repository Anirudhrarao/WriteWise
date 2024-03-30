import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message_content = data.get('content', '')
        receiver_username = data.get('receiver', '')

        if not message_content or not receiver_username:
            return

        receiver = User.objects.filter(username=receiver_username).first()
        if not receiver:
            return

        message = await self.save_message(message_content, receiver)

        # Send message to the receiver if online
        receiver_channel_name = f"user_{receiver.id}"
        await self.channel_layer.group_send(
            receiver_channel_name,
            {
                'type': 'chat.message',
                'message': message_content,
                'sender': self.user.username,
                'receiver': receiver_username,
                'timestamp': message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @staticmethod
    @database_sync_to_async
    def save_message(content, receiver):
        message = Message.objects.create(sender=self.user, receiver=receiver, content=content)
        return message
