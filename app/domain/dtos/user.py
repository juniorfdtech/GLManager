from app.serializers import Serializer


class UserDtoCreate(Serializer):
    username: str = None
    password: str = None
    v2ray_uuid: str = None
    connection_limit: int = None
    expiration_date: str = None


class UserDtoUpdate(Serializer):
    id: int = None
    username: str = None
    password: str = None
    v2ray_uuid: str = None
    connection_limit: int = None
    expiration_date: str = None


class UserDto(Serializer):
    id: int = None
    username: str = None
    password: str = None
    v2ray_uuid: str = None
    connection_limit: int = None
    expiration_date: str = None
