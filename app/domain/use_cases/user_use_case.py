import typing as t

from app.data.repositories import UserRepository
from app.domain.dtos import UserDto
from app.domain.entites import User
from app.utilities.shellscript import exec_command


class UserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create(self, user_dto: UserDto) -> t.Optional[UserDto]:
        data = self.user_repository.create(User.of(user_dto.to_dict()))
        data = data.to_dict()

        cmd_create_user = (
            'useradd --no-create-home ' '--shell /bin/false ' '--expiredate %s %s'
        ) % (data['expiration_date'].strftime('%Y-%m-%d'), data['username'])

        cmd_set_password = 'echo %s:%s | chpasswd' % (
            data['username'],
            data['password'],
        )

        exec_command(cmd_create_user)
        exec_command(cmd_set_password)
        return UserDto.of(data)

    def get_by_id(self, id: int) -> t.Optional[UserDto]:
        data = self.user_repository.get_by_id(id)
        return UserDto.of(data.to_dict())

    def get_by_username(self, username: str) -> t.Optional[UserDto]:
        data = self.user_repository.get_by_username(username)
        return UserDto.of(data.to_dict())

    def get_all(self) -> t.List[UserDto]:
        data = self.user_repository.get_all()
        return [UserDto.of(item.to_dict()) for item in data]

    def update(self, user_dto: UserDto) -> t.Optional[UserDto]:
        user_entity = User.of(user_dto.to_dict())
        data = self.user_repository.update(user_entity)
        return UserDto.of(data.to_dict())

    def delete(self, id: int) -> t.Optional[UserDto]:
        data = self.user_repository.delete(id)
        return UserDto.of(data.to_dict())
