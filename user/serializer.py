import hashlib

from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError


class UserSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    refresh = serializers.CharField(required=False)
    access = serializers.CharField(required=False)
    token = serializers.CharField(required=False)

    default_error_messages = {"bad_token": ("Token is invalid or expired")}

    def validate_login(self):
        email = self.initial_data.get("email")
        password = self.initial_data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required for login.")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"error": "Invalid username or password."})

        return {"user": user}

    def validate(self, attrs):
        self.refresh_token = attrs.get("refresh")
        self.access_token = attrs.get("access")
        self.token = attrs.get("token")
        return attrs

    def logout(self):
        try:
            token = RefreshToken(self.refresh_token)
            token.blacklist()
            cache_key = hashlib.sha256(self.token.encode()).hexdigest()
            cache.set(cache_key, "blacklisted", timeout=86400)
        except TokenError:
            self.fail("bad_token")

        if self.access_token:
            try:
                AccessToken(self.access_token).blacklist()
            except TokenError:
                self.fail("bad_token")