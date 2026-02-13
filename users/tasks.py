import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def deactivate_inactive_users():
    """
    Задача деактивации пользователей, которые не заходили более месяца.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    users_to_deactivate = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True,
        is_staff=False,  # Не деактивируем администраторов
        is_superuser=False,  # Не деактивируем суперпользователей
    )

    updated_count = users_to_deactivate.update(is_active=False)

    print(
        f"Деактивировано {updated_count} пользователей, которые не заходили более месяца."
    )  # Только для отладки

    logger.info(
        f"Деактивировано {updated_count} пользователей, которые не заходили более месяца."
    )
    return f"Деактивировано {updated_count} пользователей."
