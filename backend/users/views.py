from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAuthorOrReadOnly

from .models import CustomUser, Subscribe
from .serializers import (
    CustomUserSerializer,
    PasswordSerializer,
    SubscribeSerializer
)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для кастомного пользователя."""
    pagination_class = PageNumberPagination
    permission_classes = (AllowAny,)
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='subscriptions', url_name='subscriptions',
            permission_classes=[IsAuthorOrReadOnly])
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = user.follower.all()
        authors = [item.author.id for item in subscriptions]
        queryset = CustomUser.objects.filter(pk__in=authors)
        serializer = SubscribeSerializer(
            queryset, many=True, context={'request': request}
        )
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

    @action(methods=['post', 'delete'], detail=True,
            url_path='subscribe', url_name='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=id)
        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Нельзя подписаться на самого себя.'
                )
            if Subscribe.objects.filter(user=user,
                                        author=author).exists():
                raise exceptions.ValidationError('Подписка уже оформлена.')
            Subscribe.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscribe.objects.filter(user=user,
                                            author=author).exists():
                raise exceptions.ValidationError(
                    'Вы уже удалили подписку.'
                )
            subscription = get_object_or_404(
                Subscribe,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ChangePasswordView(CreateAPIView):
    """Изменение пароля."""
    serializer_class = PasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(
                serializer.validated_data.get('current_password')
            ):
                return Response(
                    {_('current_password'): _('Wrong password.')},
                    status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(
                serializer.validated_data.get('new_password'))
            self.object.save()
            return Response(
                {_('message'): _('Пароль успешно изменён')},
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
