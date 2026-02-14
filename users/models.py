from decimal import Decimal

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from courses.models import Course, Lesson


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Телефон"
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def is_moderator(self):
        return self.groups.filter(name=settings.MODERATOR_GROUP_NAME).exists()

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"


class Payment(models.Model):
    PAYMENT_CASH = "cash"
    PAYMENT_TRANSFER = "transfer"

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CASH, "Наличные"),
        (PAYMENT_TRANSFER, "Перевод на счёт"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="payments",
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс",
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты"
    )

    stripe_session_id = models.CharField(blank=True, null=True)
    stripe_session_url = models.URLField(max_length=500, blank=True, null=True)
    stripe_status = models.CharField(blank=True, null=True)

    def __str__(self):
        return (
            f"{self.user.email} - {self.amount} ({self.get_payment_method_display()})"
        )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
