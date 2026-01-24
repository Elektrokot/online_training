import re

from rest_framework.serializers import ValidationError


class YouTubeLinkValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Получаем значение поля из validated_data
        url = value.get(self.field)

        if url:
            # Проверяем, что ссылка начинается с YouTube
            pattern = r"^https?://(www\.)?youtube\.com/watch\?v=|^https?://youtu\.be/"
            if not re.match(pattern, url):
                raise ValidationError("Ссылка может вести только на YouTube.")
