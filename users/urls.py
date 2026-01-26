from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from courses.views import PaymentCreateView, PaymentStatusView
from users.apps import UsersConfig
from users.views import (UserDeleteView, UserListAPIView, UserRegisterView,
                         UserRetrieveUpdateAPIView)

app_name = UsersConfig.name


urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="user-detail"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("users/delete/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
    path("payments/create/", PaymentCreateView.as_view(), name="payment-create"),
    path(
        "payments/status/<str:session_id>/",
        PaymentStatusView.as_view(),
        name="payment-status",
    ),
]
