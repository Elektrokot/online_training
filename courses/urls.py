from django.urls import include, path
from rest_framework.routers import DefaultRouter

from courses.apps import CoursesConfig
from courses.views import (CourseViewSet, LessonCreateAPIView,
                           LessonDestroyAPIView, LessonListAPIView,
                           LessonRetrieveAPIView, LessonUpdateAPIView,
                           PaymentListView, SubscriptionToggleView, PaymentStatusView)

app_name = CoursesConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-retrieve"),
    path(
        "lessons/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"
    ),
    path(
        "lessons/delete/<int:pk>/", LessonDestroyAPIView.as_view(), name="lesson-delete"
    ),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path(
        "courses/<int:course_id>/subscription/",
        SubscriptionToggleView.as_view(),
        name="subscription",
    ),
    path('payments/status/<str:session_id>/', PaymentStatusView.as_view(), name='payment-status'),
]
