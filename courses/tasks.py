from datetime import timezone, timedelta
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """
    Асинхронная задача отправки email подписчикам об обновлении курса.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
        return

    # Проверка: обновлялся ли курс менее 4 часов назад
    if course.updated_at and course.updated_at > timezone.now() - timedelta(hours=4):
        print(f"Course {course_id} was updated less than 4 hours ago. Skipping notification.")
        return

    subscribers = Subscription.objects.filter(course=course, is_active=True).select_related('user')

    for sub in subscribers:
        user = sub.user
        subject = f"[Обновление] Курс '{course.title}' обновлён!"
        message = f"""
        Привет, {user.first_name or user.email}!

        Курс "{course.title}" был обновлён. Заходи и посмотри, что нового!
        """
        recipient_list = [user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
