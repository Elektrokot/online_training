from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_email(course_id):
    """
    Асинхронная задача отправки email подписчикам об обновлении курса.
    """
    course = Course.objects.get(id=course_id)

    # Проверка: обновлялся ли курс менее 4 часов назад
    if course.updated_at and course.updated_at > timezone.now() - timedelta(hours=4):
        logger.info(f"Курс {course_id} был обновлён менее 4х часов назад. Уведомления не будет.")
        print(f"Курс {course_id} был обновлён менее 4х часов назад. Уведомления не будет.") # Только для отладки
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
