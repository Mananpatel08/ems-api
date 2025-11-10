from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid token")
        return self.get_user(validated_token), validated_token
