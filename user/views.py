from .serializer import UserSerializer, CustomUserSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from services.utils import get_response


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    @action(detail=False, methods=["post"], url_path="login", url_name="user-login")
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = serializer.validate_login()
        except ValidationError as e:
            return get_response(
                message=e.detail,
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = data["user"]
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        user_data = CustomUserSerializer(user).data

        response = get_response(
            is_success=True,
            message="Login successful",
            data={
                "refresh": str(refresh),
                "access": access,
                "user": user_data,
            },
            status_code=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7 * 2,
            path="/",
        )

        return response

    @action(detail=False, methods=["post"], url_path="logout", url_name="user-logout")
    def logout(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk
        request.data["token"] = request.auth.get("jti")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.logout()
        except ValidationError as e:
            return get_response(
                message=e.detail,
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        response = get_response(is_success=True, message="Logout Successful")
        response.delete_cookie("access_token", path="/")
        return response

    @action(detail=False, methods=["post"], url_path="refresh", url_name="user-refresh")
    def refresh(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                user = OutstandingToken.objects.get(token=refresh_token).user
                RefreshToken(refresh_token).blacklist()

                new_refresh_token = RefreshToken.for_user(user)

                return get_response(
                    is_success=True,
                    message="Token refresh successfully",
                    data={
                        "access": str(new_refresh_token.access_token),
                        "refresh": str(new_refresh_token),
                    },
                )
            except Exception as e:
                return get_response(
                    message=str(e), status_code=status.HTTP_400_BAD_REQUEST
                )
        else:
            return get_response(
                message="Refresh token not provided.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False, methods=["post"], url_path="check-auth", url_name="check-auth"
    )
    def token_validity(self, request, *args, **kwargs):
        access_token_str = request.data.get("access")
        if not access_token_str:
            return get_response(
                message="Access token not provided.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            AccessToken(access_token_str)
            return get_response(
                message="Token is valid", status_code=200, is_success=True
            )

        except TokenError:
            return get_response(
                message="Token is Expired.", status_code=status.HTTP_401_UNAUTHORIZED
            )
        except Exception:
            return get_response(
                message="Invalid token.", status_code=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="me", url_name="me")
    def user_profile(self, request):
        serializer = CustomUserSerializer(request.user)
        return get_response(
            is_success=True,
            message="User profile fetched successfully.",
            data=serializer.data,
        )
