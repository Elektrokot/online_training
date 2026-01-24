from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from courses.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Load initial data: users, courses, lessons and payments"

    def handle(self, *args, **options):
        # Создаём пользователя
        user, created = User.objects.get_or_create(
            email="user1@example.com",
            defaults={
                "password": make_password("qwerty123"),
                "phone": "+79991234567",
                "city": "Москва",
            },
        )
        if created:
            self.stdout.write(f"Created user: {user.email}")

        # Создаём курс
        course, created = Course.objects.get_or_create(
            title="Python Basics",
            defaults={
                "description": "Basic Python course",
                "owner": user,
            },
        )
        if created:
            self.stdout.write(f"Created course: {course.title}")

        # Создаём урок
        lesson, created = Lesson.objects.get_or_create(
            title="Variables",
            defaults={
                "description": "Introduction to variables",
                "video_url": "https://example.com/video",
                "course": course,
                "owner": user,
            },
        )
        if created:
            self.stdout.write(f"Created lesson: {lesson.title}")

        # Создаём платежи
        payment1, created = Payment.objects.get_or_create(
            user=user,
            payment_date="2025-04-05T10:00:00Z",
            paid_course=course,
            paid_lesson=None,
            amount=1000.00,
            payment_method="transfer",
        )
        if created:
            self.stdout.write(f"Created payment 1")

        payment2, created = Payment.objects.get_or_create(
            user=user,
            payment_date="2025-04-06T11:30:00Z",
            paid_course=None,
            paid_lesson=lesson,
            amount=500.00,
            payment_method="cash",
        )
        if created:
            self.stdout.write(f"Created payment 2")

        self.stdout.write(self.style.SUCCESS("Successfully loaded all data"))
