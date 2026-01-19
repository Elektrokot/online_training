from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    preview = models.ImageField(
        upload_to="course_previews/", blank=True, null=True, verbose_name="Превью курса"
    )
    description = models.TextField(verbose_name="Описание курса")
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец курса",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока")
    preview = models.ImageField(
        upload_to="lesson_previews/", blank=True, null=True, verbose_name="Превью урока"
    )
    video_url = models.URLField(verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец урока",
    )

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
