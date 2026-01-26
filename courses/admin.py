from django.contrib import admin

from .models import Course, Lesson, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner")
    list_filter = ("owner",)
    search_fields = ("title", "description", "owner__email")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "owner")
    list_filter = ("course", "owner")
    search_fields = ("title", "description", "course__title", "owner__email")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "course")
    list_filter = ("course", "user")
    search_fields = ("user__email", "course__title")
