from django.urls import path
from .views import RegisterView, VerifyEmailView, GoogleAuthView, ResendEmailCodeView, LoginView

urlpatterns = [
  path("register/", RegisterView.as_view()),
  path("verify-email/", VerifyEmailView.as_view()),
  path("google/", GoogleAuthView.as_view()),
  path("resend-email-code/", ResendEmailCodeView.as_view()),
  path("login/", LoginView.as_view()),
]
