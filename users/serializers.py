from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already registered")
        return email

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

class ResendEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    
    
class SimpleMessageSerializer(serializers.Serializer):
  detail = serializers.CharField()


class AuthTokenResponseSerializer(serializers.Serializer):
  access = serializers.CharField()
  refresh = serializers.CharField()
