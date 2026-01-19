from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Trip, TripMessage
from .serializers import TripSerializer
from .services.deepseek import ask_deepseek, DeepSeekError
from .services.messages import build_messages_for_ai

from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    TripSerializer,
    TripChatRequestSerializer,
    TripChatResponseSerializer,
)

class TripListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="List user trips",
        responses={200: TripSerializer(many=True)},
    )
    def get(self, request):
        trips = Trip.objects.filter(user=request.user)
        return Response(TripSerializer(trips, many=True).data)

    @extend_schema(
        summary="Create a new trip",
        request=TripSerializer,
        responses={201: TripSerializer},
    )
    def post(self, request):
        serializer = TripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip = serializer.save(user=request.user)
        return Response(TripSerializer(trip).data, status=201)


class TripChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Send message to trip chat",
        description="Send a user message and receive AI response",
        request=TripChatRequestSerializer,
        responses={200: TripChatResponseSerializer},
        examples=[
            OpenApiExample(
                "User message example",
                value={"message": "Plan a 3-day trip to Rome"},
                request_only=True,
            ),
            OpenApiExample(
                "AI response example",
                value={"answer": "Here is a sample itinerary for Rome..."},
                response_only=True,
            ),
        ],
    )
    def post(self, request, trip_id):
        trip = Trip.objects.get(id=trip_id, user=request.user)

        user_message = request.data.get("message")
        if not user_message:
            return Response(
                {"detail": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        TripMessage.objects.create(
            trip=trip,
            role="user",
            content=user_message,
        )

        # messages = build_messages_for_ai(trip)
        messages = [
            {"role": "user", "content": user_message}
        ]


        try:
            ai_answer = ask_deepseek(messages)

            TripMessage.objects.create(
                trip=trip,
                role="assistant",
                content=ai_answer,
            )

            return Response({"answer": ai_answer})

        except DeepSeekError:
            return Response(
                {
                    "detail": "AI service is temporarily unavailable. Try again later."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

