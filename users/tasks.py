from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

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
        is_superuser=False  # Не деактивируем суперпользователей
    )

    count = users_to_deactivate.count()
    users_to_deactivate.update(is_active=False)

    print(f"Deactivated {count} users who haven't logged in for over a month.")
    return f"Deactivated {count} users."
