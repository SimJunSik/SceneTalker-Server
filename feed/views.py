from .models import Post, Comment, PostSerializer, CommentSerializer, Feed
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class PostListCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, feed_id):
        """
            피드의 게시물 리스트 불러오는 API

            ---
            # Path Params
                - feed_id : 피드 id
            # Query Params
                - content : 게시물 검색 내용
        """
        query_params = request.query_params.get('content')
        if query_params :
            user = request.user
            user.recent_searches.add(query_params)
        posts = Feed.objects.prefetch_related('post_set').get(id=feed_id).post_set.all()
        if query_params:
            posts = posts.filter(content__icontains=query_params)
        serializer = PostSerializer(posts, context={'request': request}, many=True)
        return Response(serializer.data)

    def post(self, request, feed_id):
        """
            피드에 게시물 등록 API

            ---
            # Path Params
                - feed : 피드 id
            # Body
                - content : 게시물 내용(Required)
                - image : image 객체
        """
        copied_request_data = request.data.copy()
        copied_request_data['feed'] = feed_id
        copied_request_data['author'] = request.user.id
        serializer = PostSerializer(data=copied_request_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
        게시물 조회 & 수정 & 삭제 API

        ---
        # Path Params
            - feed_id : 피드 id
            - id : 게시물 id
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostLikesUpdateAPIView(LoggingMixin, APIView):
    """
        게시물 좋아요 API

        ---
        # Path Params
            - feed_id : 피드 id
            - post_id : 게시물 id
    """

    def post(self, request, feed_id, post_id):
        post = Post.objects.get(id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return Response({'result': 'success'})


class CommentListCreateAPIView(LoggingMixin, APIView):
    def get(self, request, feed_id, post_id):
        """
            게시물의 댓글 리스트 불러오는 API

            ---
            # Path Params
                - feed_id : 피드 id
                - post_id : 게시물 id
        """
        comments = Post.objects.prefetch_related('comment_set').get(id=post_id).comment_set.all()
        serializer = CommentSerializer(comments, context={'request': request}, many=True)
        return Response(serializer.data)

    def post(self, request, feed_id, post_id):
        """
            게시물에 댓글 등록하는 API

            ---
            # Path Params
                - feed_id : 피드 id
                - post_id : 게시물 id
            # Body
                - content : 댓글 내용(Required)
        """
        request.data['post'] = post_id
        request.data['author'] = request.user.id
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentRetrieveUpdateDestroyAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """
        댓글 조회 & 수정 & 삭제 API

        ---
        # Path Params
            - feed_id : 피드 id
            - post_id : 게시물 id
            - id : 댓글 id
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
