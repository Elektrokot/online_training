from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "phone",
        "city",
        "is_active",
        "date_joined",
    )  # Убрали 'created_at'
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("email", "phone", "city")
    ordering = ("email",)

    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = BaseUserAdmin.add_fieldsets


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "payment_date",
        "paid_course",
        "paid_lesson",
        "amount",
        "payment_method",
    )
    list_filter = ("payment_method", "payment_date")
    search_fields = ("user__email", "paid_course__title", "paid_lesson__title")
    readonly_fields = ("payment_date",)
