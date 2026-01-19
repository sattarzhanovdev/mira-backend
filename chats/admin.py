from django.contrib import admin
from .models import Trip, TripMessage


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "destination",
        "user",
        "status",
        "created_at",
    )
    search_fields = ("title", "destination", "user__email")


@admin.register(TripMessage)
class TripMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "role", "created_at")
