from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from drama.models import Drama

# Create your models here.
class TaggedRecentSearches(TaggedItemBase):
    content_object = models.ForeignKey('User', on_delete=models.CASCADE)

class User(AbstractUser) :

    profile_image = models.ImageField(null=True, blank=True, upload_to='user_profile_image/')
    drama_bookmark = models.ManyToManyField(Drama, blank=True)
    recent_searches = TaggableManager(through=TaggedRecentSearches, related_name='recent_searches')

    def __str__(self) :
        return '이메일 : {} , 닉네임 : {}'.format(self.email, self.username)
