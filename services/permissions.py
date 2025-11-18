from rest_framework.exceptions import PermissionDenied
from functools import wraps
from user.enums import UserRoleEnum


def allow_permission(allowed_roles: list[UserRoleEnum]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user = request.user

            if not user or not user.is_authenticated:
                raise PermissionDenied("Authentication required.")

            if getattr(user, "is_super_admin", False):
                return view_func(self, request, *args, **kwargs)

            user_role = getattr(user, "user_role", None)

            allowed_values = [
                role.value if hasattr(role, "value") else role for role in allowed_roles
            ]

            if user_role not in allowed_values:
                raise PermissionDenied(
                    "You do not have permission to access this resource."
                )

            return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator
