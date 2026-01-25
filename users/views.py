from rest_framework import generics, status
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserPrivateSerializer,
    UserPublicSerializer,
    UserRegisterSerializer,
)


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer

    def get_serializer_class(self):
        # Если пользователь просматривает/редактирует **свой** профиль
        if self.request.user == self.get_object():
            return UserPrivateSerializer
        # Иначе — общий сериализатор
        return UserPublicSerializer

    def check_object_permissions(self, request, obj):
        # Проверяем, может ли пользователь редактировать объект
        if request.method in ["PUT", "PATCH"] and request.user != obj:
            self.permission_denied(
                request, message="You can only edit your own profile."
            )
        return super().check_object_permissions(request, obj)


class UserRegisterView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class UserDeleteView(APIView):  # Класс удаления пользователя доступен только админу
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
