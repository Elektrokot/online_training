from urllib.parse import urlparse

from rest_framework.serializers import ValidationError


class YouTubeLinkValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Получаем значение поля из validated_data
        url = value.get(self.field)

        if url:
            # Проверяем, что ссылка начинается с YouTube
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            if domain not in ["www.youtube.com", "youtube.com", "youtu.be"]:
                raise ValidationError("Ссылка может вести только на YouTube.")
