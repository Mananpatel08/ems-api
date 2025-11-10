from enum import Enum


class UserRoleEnum(Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    USER = "USER"

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]
