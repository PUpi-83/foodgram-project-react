from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from api.pagination import CustomPageNumberPagination

from .models import CustomUser, Follow
from .serializers import CustomUserSerializer, FollowSerializer


class CustomUserViewSet(UserViewSet):
    """Представление для пользователей."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(CustomUser, id=author_id)

        if self.request.method == 'POST':
            serializer = FollowSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            subscription = get_object_or_404(
                Follow, user=user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=CustomPageNumberPagination
    )
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
