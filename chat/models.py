from django.db import models
from django.contrib.auth import get_user_model
from drama.models import DramaEachEpisode

User = get_user_model()
# Create your models here.
class ChatMessage(models.Model) :

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    drama_each_episode = models.ForeignKey(DramaEachEpisode, on_delete=models.SET_NULL, null=True)
    message = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) :
        return "드라마 : {}, 회차 : {}, 메세지 : {}".format(self.drama_each_episode.drama.title, 
                                                            self.drama_each_episode.episode,
                                                            self.message)