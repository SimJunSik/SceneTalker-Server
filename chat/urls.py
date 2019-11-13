from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('<str:room_name>/<str:user_name>/', views.room, name='room'),
    path('count/<int:drama_id>/<int:episode>/', view=views.GetDramaEachEpisodeCount.as_view()),
]
