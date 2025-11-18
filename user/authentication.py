import hashlib

from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated


class CustomUserIsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False
        is_allowed_user = True
        token = request.auth.get("jti")
        cache_key = hashlib.sha256(token.encode()).hexdigest()
        cached_data = cache.get(cache_key)
        if cached_data:
            raise AuthenticationFailed("Token is expired")
        else:
            is_allowed_user = True
        return is_allowed_user
