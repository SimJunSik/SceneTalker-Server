from django.db import models
from django.contrib.auth.models import AbstractUser
from drama.models import Drama

# Create your models here.
class User(AbstractUser) :

    profile_image = models.ImageField(null=True, blank=True, upload_to='user_profile_image/', default='user_profile_image_default.png')
    name = models.CharField(max_length=255)
    drama_bookmark = models.ManyToManyField(Drama, blank=True)

    def __str__(self) :
        return self.username