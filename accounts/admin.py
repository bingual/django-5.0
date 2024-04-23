from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["username", "email"]
    list_display = [
        "pk",
        "username",
        "email",
        "is_superuser",
        "is_staff",
        "is_active",
    ]
    list_display_links = ["username", "email"]
    list_filter = ["is_superuser", "is_staff", "is_active"]
