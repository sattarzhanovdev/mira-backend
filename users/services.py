from django.core.mail import send_mail
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils import timezone
from django.utils.crypto import get_random_string
from .models import EmailVerificationCode

def send_verification_email(email: str, code: str):
    send_mail(
        subject="Подтверждение регистрации",
        message=f"Ваш код подтверждения: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

def verify_google_token(token: str) -> dict:
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        return idinfo
    except Exception:
        return None
      

RESEND_TIMEOUT_SECONDS = 60


def can_resend_code(user) -> bool:
    last_code = (
        EmailVerificationCode.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    if not last_code:
        return True

    delta = timezone.now() - last_code.created_at
    return delta.total_seconds() >= RESEND_TIMEOUT_SECONDS


def resend_verification_code(user):
    # помечаем старые коды как использованные
    EmailVerificationCode.objects.filter(
        user=user,
        is_used=False,
    ).update(is_used=True)

    code = get_random_string(6, allowed_chars="0123456789")

    EmailVerificationCode.objects.create(
        user=user,
        code=code,
    )

    return code