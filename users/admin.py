from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_email_verified", "is_staff")
    search_fields = ("email",)
