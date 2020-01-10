from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "user"
urlpatterns = [
    path("authenticate/", view = views.GetUserByToken.as_view()),
    path("unregistration/", view = views.UnRegistrationUser.as_view()),
    path("check-duplicated/", view = views.CheckUsernameIsDuplicated.as_view()),
    path("bookmark-best-drama/", view = views.GetRealTimeUserBestDrama.as_view()),
    path("bookmark-dramas/", view = views.GetUserBookmarkDramaList.as_view()),
    path("posts/write/", view = views.GetUserWritePostList.as_view()),
    path("posts/like/", view = views.GetUserLikePostList.as_view()),
    path("change/username/", view = views.ChangeUsername.as_view()),
    path("profile-image/", view = views.PutUserProfileImage.as_view()),
    path("recent-searches/", view = views.UserRecentSearchesAPIView.as_view()),

    path("<str:username>/", view = views.UserViewSet.as_view()),
    path("<int:drama_id>/bookmark/", view = views.ToggleDramaBookmark.as_view()),
]