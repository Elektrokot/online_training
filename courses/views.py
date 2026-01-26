from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Payment
from users.serializers import PaymentCreateSerializer

from .models import Course, Lesson, Subscription
from .paginators import CoursePagination, LessonPagination
from .permissions import IsModeratorOrReadOnly, IsOwner
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer
from .services.stripe_service import (create_checkout_session,
                                      create_stripe_price,
                                      create_stripe_product,
                                      get_checkout_session_status)


@extend_schema(
    description="API для управления курсами: создание, просмотр, обновление, удаление.",
    tags=["Courses"],
)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = CoursePagination  # Добавляем пагинацию

    def get_queryset(self):
        user = self.request.user

        if user.is_moderator:
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action in ["create"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated, IsModeratorOrReadOnly]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsModeratorOrReadOnly | IsOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(description="API для создания урока.", tags=["Lessons"])
class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(description="API для просмотра списка уроков.", tags=["Lessons"])
class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrReadOnly]
    pagination_class = LessonPagination  # Добавляем пагинацию

    def get_queryset(self):
        user = self.request.user

        if user.is_moderator:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


@extend_schema(description="API для просмотра урока.", tags=["Lessons"])
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrReadOnly]


@extend_schema(description="API для обновления урока.", tags=["Lessons"])
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrReadOnly | IsOwner]


@extend_schema(description="API для удаления урока.", tags=["Lessons"])
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


@extend_schema(
    description="API для просмотра списка платежей с фильтрацией и сортировкой.",
    tags=["Payments"],
)
class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]


@extend_schema(
    description="API для оплаты курсов или уроков.",
    tags=["Payments"],
)
class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        # Создаём продукт в Stripe
        product_id = create_stripe_product(
            payment.paid_course.title
            if payment.paid_course
            else payment.paid_lesson.title
        )

        # Создаём цену в Stripe (умножаем на 100, т.к. в копейках)
        price_id = create_stripe_price(product_id, int(payment.amount * 100))

        # Создаём сессию оплаты
        session_id, session_url = create_checkout_session(
            price_id,
            success_url="http://127.0.0.1:8000/payment-success/",
            cancel_url="http://127.0.0.1:8000/payment-cancel/",
        )

        # Сохраняем данные сессии в модель
        payment.stripe_session_id = session_id
        payment.stripe_session_url = session_url
        payment.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        payment = serializer.instance

        # Возвращаем только session_url
        return Response(
            {"session_url": payment.stripe_session_url}, status=status.HTTP_201_CREATED
        )


@extend_schema(
    description="API для контроля статуса платежа.",
    tags=["Payments"],
)
class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        payment = Payment.objects.filter(
            stripe_session_id=session_id, user=request.user
        ).first()
        if not payment:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        status_result = get_checkout_session_status(session_id)
        return Response({"status": status_result}, status=status.HTTP_200_OK)


@extend_schema(
    description="API для подписки или отписки от курса.",
    tags=["Subscriptions"],
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
)
class SubscriptionToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course, id=course_id)

        # Ищем подписку
        sub, created = Subscription.objects.get_or_create(user=user, course=course)

        if not created:
            # Подписка уже была — удаляем
            sub.delete()
            message = "Подписка удалена"
        else:
            # Подписка создана
            message = "Подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
