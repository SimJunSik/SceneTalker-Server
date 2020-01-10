from django.db import models
from django.conf import settings
from rest_framework import serializers
from drama.models import Drama
from feed.utils.imagepath import user_directory_path


class Feed(models.Model):
    drama = models.OneToOneField(Drama, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.drama.title)


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = '__all__'


class Post(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(blank=True, upload_to=user_directory_path)  # s3에 올라가게 해야함
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def user_profile_image(self):
        try :
            return self.author.profile_image.url
        except :
            return None

    @property
    def post_drama_title(self):
        return self.feed.drama.title

    @property
    def like_counts(self):
        return self.likes.all().count()

    @property
    def comment_counts(self):
        return self.comment_set.all().count()

    def __str__(self):
        return '{} - {}'.format(self.feed.drama, self.content[:10])


class PostSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()
    is_liked_by_me = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'feed',
            'author',
            'content',
            'image',
            'likes',
            'created_at',
            'updated_at',
            'like_counts',
            'comment_counts',
            'is_mine',
            'is_liked_by_me',
            'author_name',
            'post_drama_title',
            'user_profile_image',
        )

    def get_is_mine(self, obj):
        request_user = self.context['request'].user
        return obj.author == request_user

    def get_is_liked_by_me(self, obj):
        request_user = self.context['request'].user
        return request_user in obj.likes.all()

    def get_author_name(self, obj):
        return obj.author.username


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '{} - {}'.format(self.post.content, self.content)

    @property
    def user_profile_image(self):
        try :
            return self.author.profile_image.url
        except :
            return None
    
    @property
    def feed_id(self) :
        return self.post.feed.id


class CommentSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'post',
            'author',
            'content',
            'created_at',
            'updated_at',
            'feed_id',
            'is_mine',
            'author_name',
            'user_profile_image',
        )

    def get_is_mine(self, obj):
        request_user = self.context['request'].user
        return obj.author == request_user

    def get_author_name(self, obj):
        return obj.author.username