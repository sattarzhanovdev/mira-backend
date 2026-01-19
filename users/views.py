from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema

from .models import User, EmailVerificationCode
from .services import (
    send_verification_email,
    verify_google_token,
    can_resend_code,
    resend_verification_code,
)
from .serializers import (
    RegisterSerializer,
    VerifyEmailSerializer,
    LoginSerializer,
    ResendEmailCodeSerializer,
    AuthTokenResponseSerializer,
    SimpleMessageSerializer,
)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register user by email",
        request=RegisterSerializer,
        responses={201: SimpleMessageSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        code = get_random_string(6, allowed_chars="0123456789")
        EmailVerificationCode.objects.create(user=user, code=code)

        send_verification_email(user.email, code)

        return Response(
            {"detail": "Verification code sent to email"},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verify email with OTP code",
        request=VerifyEmailSerializer,
        responses={200: SimpleMessageSerializer},
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        record = EmailVerificationCode.objects.filter(
            user=user,
            code=code,
            is_used=False,
        ).order_by("-created_at").first()

        if not record or record.is_expired():
            return Response(
                {"detail": "Invalid or expired code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record.is_used = True
        record.save()
        user.is_email_verified = True
        user.save()

        return Response({"detail": "Email successfully verified"})


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login with email and password",
        request=LoginSerializer,
        responses={
            200: AuthTokenResponseSerializer,
            401: SimpleMessageSerializer,
            403: SimpleMessageSerializer,
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_email_verified:
            return Response(
                {"detail": "Email not verified"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(generate_tokens(user))


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login with Google",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id_token": {"type": "string"},
                },
                "required": ["id_token"],
            }
        },
        responses={200: AuthTokenResponseSerializer},
    )
    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response(
                {"detail": "id_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = verify_google_token(token)
        if not payload:
            return Response(
                {"detail": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, _ = User.objects.get_or_create(
            email=payload["email"],
            defaults={
                "google_id": payload["sub"],
                "is_email_verified": True,
            },
        )

        return Response(generate_tokens(user))

      
class ResendEmailCodeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Resend email verification code",
        request=ResendEmailCodeSerializer,
        responses={200: SimpleMessageSerializer},
    )
    def post(self, request):
        serializer = ResendEmailCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email=serializer.validated_data["email"]
        ).first()

        if not user:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_email_verified:
            return Response(
                {"detail": "Email already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not can_resend_code(user):
            return Response(
                {"detail": "Try again later"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        code = resend_verification_code(user)
        send_verification_email(user.email, code)

        return Response({"detail": "Verification code resent"})
