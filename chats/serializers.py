from rest_framework import serializers
from .models import Trip, TripMessage


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = (
            "id",
            "title",
            "destination",
            "start_date",
            "end_date",
            "travelers_count",
            "budget",
            "status",
            "created_at",
        )


class TripMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripMessage
        fields = (
            "id",
            "role",
            "content",
            "created_at",
        )


# 🔽 ДОБАВЬ ВНИЗ (НОВОЕ)


class TripChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        help_text="User message sent to AI"
    )


class TripChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField(
        help_text="AI-generated response"
    )