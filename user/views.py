from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from services.pagination import CustomPagination
from services.utils import get_response
from services.permissions import allow_permission

from .authentication import CustomUserIsAuthenticated
from .enums import UserRoleEnum
from .models import CustomUser
from .serializer import (
    UserSerializer,
    CustomUserSerializer,
    CustomUserLiteSerializer,
)


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [CustomUserIsAuthenticated]
    serializer_class = UserSerializer

    filter_backends = [SearchFilter]
    search_fields = [
        "first_name",
        "last_name",
        "email",
    ]

    @action(
        detail=False,
        methods=["post"],
        url_path="login",
        url_name="user-login",
        permission_classes=[AllowAny],
    )
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
        refresh["user_role"] = user.user_role

        access = str(refresh.access_token)
        user_data = CustomUserLiteSerializer(user, context={"request": request}).data

        return get_response(
            is_success=True,
            message="Login successful",
            data={
                "refresh": str(refresh),
                "access": access,
                "user": user_data,
            },
            status_code=status.HTTP_200_OK,
        )

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

        return get_response(is_success=True, message="Logout Successful")

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

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        url_name="me",
    )
    def user_profile(self, request):
        serializer = CustomUserLiteSerializer(
            request.user, context={"request": request}
        )
        return get_response(
            is_success=True,
            message="User profile fetched successfully.",
            data=serializer.data,
        )

    @action(
        detail=False,
        methods=["put", "patch"],
        url_path="update-profile",
        url_name="update-profile",
    )
    def update_profile(self, request):
        serializer = CustomUserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return get_response(
                is_success=True,
                message="Profile updated successfully.",
                data=serializer.data,
            )

        return get_response(
            is_success=False,
            status_code=400,
            message="Validation error.",
            errors=serializer.errors,
        )

    @action(methods=["post"], detail=False, url_path="add", url_name="add")
    @allow_permission([UserRoleEnum.SUPER_ADMIN])
    @transaction.atomic
    def create_user(self, request):
        try:
            data = request.data

            email = data.get("email")
            if not email:
                return get_response(
                    is_success=False,
                    message="Email is required.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if CustomUser.objects.filter(email=email).exists():
                return get_response(
                    is_success=False,
                    message="This email already exists.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            password = data.get("password") or "Wedo@123"

            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_role=UserRoleEnum.USER.value,
                is_active=True,
            )

            serializer = CustomUserSerializer(user, context={"request": request})

            return get_response(
                is_success=True,
                message="User created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return get_response(
                is_success=False,
                message="Error creating user.",
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=False, url_path="users", url_name="users")
    @allow_permission([UserRoleEnum.SUPER_ADMIN])
    def list_user(self, request):
        queryset = CustomUser.objects.filter(
            user_role=UserRoleEnum.USER.value,
            is_active=True,
            is_superuser=False,
        )

        queryset = self.filter_queryset(queryset)

        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = CustomUserLiteSerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(
                serializer.data, message="Users fetched successfully."
            )

        serializer = CustomUserLiteSerializer(
            queryset, many=True, context={"request": request}
        )
        return get_response(
            is_success=True,
            message="Users fetched successfully.",
            data=serializer.data,
        )

    @action(
        methods=["get"],
        detail=False,
        url_path="retrieve-user/(?P<user_id>[^/.]+)",
        url_name="retrieve-user",
    )
    @allow_permission([UserRoleEnum.SUPER_ADMIN])
    def retrieve_user(self, request, user_id=None):
        try:
            user = CustomUser.objects.get(
                id=user_id,
                is_active=True,
            )

            serializer = CustomUserLiteSerializer(user, context={"request": request})
            return get_response(
                is_success=True,
                message="User retrieved successfully.",
                data=serializer.data,
            )

        except CustomUser.DoesNotExist:
            return get_response(
                is_success=False,
                message="User not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return get_response(
                is_success=False,
                message="Error retrieving user.",
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
