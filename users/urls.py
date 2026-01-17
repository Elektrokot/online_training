from django.urls import path
from rest_framework.routers import DefaultRouter
from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserUpdateAPIView, UserDestroyAPIView, UserListAPIView, UserRetrieveAPIView, \
    UserViewSet

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='users-list'),
    path('users/create/', UserCreateAPIView.as_view(), name='users-create'),
    path('users/<int:pk>/', UserRetrieveAPIView.as_view(), name='users-retrieve'),
    path('users/update/<int:pk>/', UserUpdateAPIView.as_view(), name='users-update'),
    path('users/delete/<int:pk>/', UserDestroyAPIView.as_view(), name='users-delete'),
] + router.urls
