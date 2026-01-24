from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from courses.models import Course, Lesson


class Command(BaseCommand):
    help = "Creates Moderator group with specific permissions"

    def handle(self, *args, **options):
        # Создаём группу
        group, created = Group.objects.get_or_create(name="Модераторы")
        if created:
            self.stdout.write(self.style.SUCCESS('Group "Модераторы" created'))

        # Получаем типы контента
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Разрешения для модераторов: просмотр и изменение (но не создание и не удаление)
        perms = [
            "view_course",
            "change_course",
            "view_lesson",
            "change_lesson",
        ]

        for perm_codename in perms:
            # Ищем разрешение по кодовому имени и типу контента
            if perm_codename.endswith("course"):
                content_type = course_content_type
            else:
                content_type = lesson_content_type

            try:
                perm = Permission.objects.get(
                    codename=perm_codename, content_type=content_type
                )
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Permission {perm_codename} does not exist")
                )

        self.stdout.write(self.style.SUCCESS("Moderator group permissions set"))
