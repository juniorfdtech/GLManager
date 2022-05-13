from app.serializers import Serializer

class UserDto(Serializer):
    username: str = None
    password: str = None
    connection_limit: int = None
    expiration_date: str = None