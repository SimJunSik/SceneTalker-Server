from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.http import JsonResponse
from channels.layers import get_channel_layer
from rest_framework.views import APIView
from drama.models import *
from .models import ChatMessage
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def room(request, drama_id, episode, user_name):

    current_user = user_name

    context = {
                'room_name_json' : mark_safe(json.dumps(drama_id)), 
                'episode' : mark_safe(json.dumps(episode)), 
                'current_user_name_json' : mark_safe(json.dumps(current_user)),
                'current_user' : current_user 
                }

    return render(request, 'chat/room.html', context)

class GetDramaEachEpisodeCount(APIView) :

    def get(self, request, drama_id, episode, format=None) :
        try :
            drama_each_episode = DramaEachEpisode.objects.get(drama__id=drama_id, episode=episode)
        except :
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = DramaEachEpisodeSerializer(drama_each_episode)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

class SaveChatMessage(APIView) :

    def post(self, request, format=None) :

        token = Token.objects.get(key=request.data['token'])
        user = User.objects.get(id=token.user_id)
        drama_each_episode = DramaEachEpisode.objects.get(drama__id=request.data['drama_id'],
                                                            episode=request.data['episode'])
        message = request.data['message']

        new_chat_message = ChatMessage.objects.create(
            creator=user,
            message=message,
            drama_each_episode=drama_each_episode
        )

        return Response(status=status.HTTP_200_OK)