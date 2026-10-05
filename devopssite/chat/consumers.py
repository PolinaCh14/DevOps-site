import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import Message
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope["user"]
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']
        self.receiver = await self.get_user_by_id(self.receiver_id)

        if not self.sender.is_authenticated or not self.receiver:
            await self.close()
            return

        self.room_name = f'chat_{min(self.sender.id, self.receiver.id)}_{max(self.sender.id, self.receiver.id)}'
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await self.get_message_history(self.sender, self.receiver)

        for message in messages:
            await self.send(text_data=json.dumps(message))

    @staticmethod
    async def get_message_history(user1, user2):
        @sync_to_async
        def fetch_messages():
            messages = Message.objects.filter(
                sender__in=[user1, user2],
                receiver__in=[user1, user2]
            ).select_related('sender').order_by('timestamp')

            # Перетворюємо в список словників
            return [
                {
                    'message': msg.content,
                    'sender': msg.sender.name,
                    'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'history': True
                }
                for msg in messages
            ]

        return await fetch_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.save_message(self.sender, self.receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.sender.name,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @staticmethod
    async def get_user_by_id(user_id):
        try:
            return await sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    async def save_message(sender, receiver, message):
        return await sync_to_async(Message.objects.create)(
            sender=sender, receiver=receiver, content=message
        )
