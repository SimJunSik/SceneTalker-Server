from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rest_framework.response import Response
from rest_framework import status
from .models import *
from drama.models import *
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    def set_count(self, channel_layer, group_name, count_value) :

        drama_each_episode = DramaEachEpisode.objects.get(drama__id=self.drama_id, 
                                                                episode=self.episode)
        count = 0
        if 'soda' in group_name :
            count = getattr(channel_layer, group_name, drama_each_episode.soda_count)
        elif 'potato' in group_name :
            count = getattr(channel_layer, group_name, drama_each_episode.sweet_potato_count)

        setattr(channel_layer, group_name, count + count_value)

        return count

    def get_user(self):
        return User.objects.get(id=self.user_id)

    def get_darama_each_episode(self):
        drama_each_episode = DramaEachEpisode.objects.get(drama__id=self.drama_id, 
                                                        episode=self.episode)
        return drama_each_episode

    async def connect(self):
        self.drama_id = self.scope['url_route']['kwargs']['drama_id']
        self.episode = self.scope['url_route']['kwargs']['episode']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user = await database_sync_to_async(self.get_user)()
        self.user_name = self.user.username
        self.room_group_name = 'chat_%s' % self.drama_id
        
        count = self.set_count(self.channel_layer, self.room_group_name, 1)

        print("join", self.channel_layer, self.room_group_name, self.user_name, self.episode, count + 1)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        count = self.set_count(self.channel_layer, self.room_group_name, -1)

        if count - 1 == 0 :
            delattr(self.channel_layer, self.room_group_name)

        # print("Leave", count - 1)
        # print("Close Code :", close_code)
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        _type = text_data_json['type']
        # print(_type)
        if _type == 'chat_message' :
            message = text_data_json['message']
            sender = self.user_name

            # print("Receive message from WebSocket")

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender
                }
            )
        elif _type == 'count' :
            kind = text_data_json['kind']

            count = self.set_count(self.channel_layer, self.room_group_name + kind, 1)

            # print(self.room_group_name, kind, count + 1)

            self.drama_each_episode = self.get_darama_each_episode()
            
            if kind == 'soda' :
                self.drama_each_episode.soda_count = count
            elif kind == 'potato' :
                self.drama_each_episode.sweet_potato_count = count

            self.drama_each_episode.save()

            # print(drama_each_episode)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'kind': str(kind),
                    'message': str(count),
                    'sender': 'AdminServer'
                }
            )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = self.user_name
        if sender == 'AdminServer' :
            kind = event['kind']
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'sender': sender,
                'kind': kind
            }))
        else :
            # print("Receive message from room group", sender, receiver)

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'sender': sender
            }))
