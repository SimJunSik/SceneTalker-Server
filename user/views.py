from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from user.serializers import UserSerializer, UserRecentSearchesSerializer
from drama.models import *
from feed.models import PostSerializer

User = get_user_model()

class UserViewSet(APIView) :

    def get_user(self, username) :

        try :
            found_user = User.objects.get(username=username)
            return found_user

        except User.DoesNotExist :
            return None

    def get(self, request, username, format=None) :

        found_user = self.get_user(username)

        if found_user is None :
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(found_user)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

class GetUserByToken(APIView):

    def post(self, request):

        """
            넘겨준 Token에 해당하는 User의 pk, Username, Email을 넘겨줌

            # Body
                - token
        """

        token = Token.objects.get(key=request.data['token'])
        user = User.objects.get(id=token.user_id)
        serializer = UserSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ToggleDramaBookmark(APIView) :

    def post(self, request, drama_id, format=None) :

        """
            드라마 북마크 상태 toggle

            # Header
                - Authorization : Token
            # Path Params
                - drama_id : 드라마 id
        """

        user = request.user

        try :
            drama = Drama.objects.get(id=drama_id)

        except Drama.DoesNotExist :
            return Response({"description" : "NOT FOUND"},status=status.HTTP_404_NOT_FOUND)

        if drama in user.drama_bookmark.all() :
            user.drama_bookmark.remove(drama)
            result = {
                "result" : "OK",
                "description" : "remove"
            }
        else :
            user.drama_bookmark.add(drama)
            result = {
                "result" : "OK",
                "description" : "add"
            }

        user.save()

        return Response(result,status=status.HTTP_200_OK)

class GetRealTimeUserBestDrama(APIView) :

    def get(self, request, format=None) :

        """
            현재 방영중인 드라마 중에서 가장 시청률이 높은 드라마 정보

            # Header
                - Authorization : Token
        """

        user = request.user

        user_drama_best_bookmark = user.drama_bookmark.filter(is_broadcasting=True).first()

        serializer = BookmarkDramaSerializer(user_drama_best_bookmark)

        print(user_drama_best_bookmark)

        return Response(serializer.data, status=status.HTTP_200_OK)

class GetUserBookmarkDramaList(APIView) :

    def get(self, request, format=None) :

        """
            유저가 "북마크" 한 드라마 리스트

            # Header
                - Authorization : Token
        """

        user = request.user

        user_drama_bookmarks = user.drama_bookmark.all()

        serializer = DramaSerializer(user_drama_bookmarks, many=True, context={'request': request})

        print(user_drama_bookmarks)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

class GetUserWritePostList(APIView) :

    def get(self, request, format=None) :

        """
            유저가 "작성" 한 게시물 리스트

            # Header
                - Authorization : Token
        """

        user = request.user

        user_write_posts = user.post_set.all()

        serializer = PostSerializer(user_write_posts, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class GetUserLikePostList(APIView) :

    def get(self, request, format=None) :

        """
            유저가 "좋아요" 한 게시물 리스트

            # Header
                - Authorization : Token
        """

        user = request.user

        user_like_posts = user.likes.all()

        serializer = PostSerializer(user_like_posts, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class ChangeUsername(APIView) :

    def put(self, request, format=None) :

        """
            유저 닉네임 변경

            # Header
                - Authorization : Token
            # Body
                - username
        """

        user = request.user

        new_username = request.data

        if new_username in list(User.objects.values_list("username", flat=True)) :
            result = {
                "result" : "duplicated"
            }
            return Response(result, status=status.HTTP_304_NOT_MODIFIED)
        else :
            user.username = new_username
            user.save()
            result = {
                "result" : "ok"
            }
            return Response(result, status=status.HTTP_200_OK)

class UnRegistrationUser(APIView) :

    def put(self, request, format=None) :

        """
            회원탈퇴

            # Header
                - Authorization : Token 
        """

        user = request.user

        User.objects.filter(pk=user.pk).update(is_active=False, email="None")

        return Response(status=status.HTTP_200_OK)

class CheckUsernameIsDuplicated(APIView) :

    def post(self, request, format=None) :

        """
            회원가입 시 닉네임 중복 체크

            # Body
                - username

            # Response
                - 중복 O : {"result" : "duplicated"}
                - 중복 X : {"result" : "ok"}
        """

        username = request.data

        if username in list(User.objects.values_list("username", flat=True)) :
            return Response({"result" : "duplicated"})

        else :
            return Response({"result" : "ok"})

class PutUserProfileImage(APIView) :

    def put(self, request, format=None) :

        """
            유저 프로필 사진 업데이트

            # Header
                - Authorization : Token

            # Body
                - file : image-file
        """

        user = request.user

        file_obj = request.data['file']

        user.profile_image = file_obj
        user.save()

        return Response({"result" : "ok"},status=status.HTTP_200_OK)

class UserRecentSearchesAPIView(APIView) :

    def get(self, request, format=None) :

        user = request.user

        serializer = UserRecentSearchesSerializer(user)

        return Response(data=serializer.data ,status=status.HTTP_200_OK)

    def delete(self, request, format=None) :

        user = request.user

        search_word = request.data.get("search_word")

        if search_word == '' :
            user.recent_searches.clear()

        user.recent_searches.remove(search_word)

        return Response({"result" : "OK"}, status=status.HTTP_200_OK)