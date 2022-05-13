import datetime
import typing as t

from console import Console, FuncItem, COLOR_NAME
from console.formatter import create_menu_bg
from app.utilities.logger import logger
from app.utilities.utils import exec_command
from app.repositories import UserRepository
from app.dtos import UserDto


def validate_username(username) -> bool:
    if not username:
        logger.error('Nome de usuário não informado')
        return False

    if len(username) < 3:
        logger.error('Nome de usuário deve conter no mínimo 3 caracteres')
        return False

    if len(username) > 20:
        logger.error('Nome de usuário deve conter no máximo 20 caracteres')
        return False

    if not username.isalnum():
        logger.error('Nome de usuário deve conter apenas letras e números')
        return False

    # if find_user_by_name(username):
    #     logger.error('Nome de usuário já existe')
    #     return False

    return True


def validate_password(password) -> bool:
    if not password:
        logger.error('Senha não informada')
        return False

    if len(password) < 3:
        logger.error('Senha deve conter no mínimo 3 caracteres')
        return False

    if len(password) > 20:
        logger.error('Senha deve conter no máximo 20 caracteres')
        return False

    if not password.isalnum():
        logger.error('Senha deve conter apenas letras e números')
        return False

    return True


def validate_connection_limit(limit) -> bool:
    if not limit:
        logger.error('Limite de conexões não informado')
        return False

    if not limit.isdigit():
        logger.error('Limite de conexões deve conter apenas números')
        return False

    if int(limit) < 1:
        logger.error('Limite de conexões deve ser maior que 0')
        return False

    return True


def validate_expiration_date(date: str) -> bool:
    if not date:
        logger.error('Data de expiração não informada')
        return False

    try:
        datetime.datetime.strptime(date, '%d/%m/%Y')
    except ValueError:
        logger.error('Data de expiração inválida')
        return False

    return True


def days_to_date(days: int) -> str:
    return (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%d/%m/%Y')


class UserInputData:
    def __init__(
        self,
        username: t.Optional[str] = None,
        password: t.Optional[str] = None,
        connection_limit: t.Optional[str] = None,
        expiration_date: t.Optional[str] = None,
    ):
        self._username = username
        self._password = password
        self._connection_limit = connection_limit
        self._expiration_date = expiration_date

    @property
    def username(self):
        while not self._username:
            self._username = input('Nome de usuário: ')
            if not validate_username(self._username):
                self._username = None

        return self._username

    @username.setter
    def username(self, value):
        if validate_username(value):
            self._username = value

    @property
    def password(self):
        while not self._password:
            self._password = input('Senha: ')
            if not validate_password(self._password):
                self._password = None

        return self._password

    @password.setter
    def password(self, value):
        if validate_password(value):
            self._password = value

    @property
    def connection_limit(self):
        while not self._connection_limit:
            self._connection_limit = input('Limite de conexões: ')
            if not validate_connection_limit(self._connection_limit):
                self._connection_limit = None

        return self._connection_limit

    @connection_limit.setter
    def connection_limit(self, value):
        if validate_connection_limit(value):
            self._connection_limit = value

    @property
    def expiration_date(self):
        while not self._expiration_date:
            self._expiration_date = input('Data de expiração: ')
            if (
                self._expiration_date.isdigit()
                and int(self._expiration_date) > 0
                and int(self._expiration_date) < 365
            ):
                self._expiration_date = days_to_date(int(self._expiration_date))

            if not validate_expiration_date(self._expiration_date):
                self._expiration_date = None

        return self._expiration_date

    @expiration_date.setter
    def expiration_date(self, value):
        if validate_expiration_date(value):
            self._expiration_date = value

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'connection_limit': self.connection_limit,
            'expiration_date': datetime.datetime.strptime(
                self.expiration_date, '%d/%m/%Y'
            ).utcnow(),
        }

    @classmethod
    def of(cls, data: t.Dict[str, t.Any]) -> 'UserInputData':
        if not data or not isinstance(data, dict):
            raise ValueError('Dados não informados')

        return cls(
            username=data.get('username'),
            password=data.get('password'),
            connection_limit=data.get('connection_limit'),
            expiration_date=data.get('expiration_date'),
        )


class UserManager:
    def __init__(self, user_input_data: UserInputData):
        if not user_input_data or not isinstance(user_input_data, UserInputData):
            raise ValueError('UserInputData não informado')

        if not user_input_data.username:
            raise ValueError('Nome de usuário não informado')

        self._user_input_data = user_input_data
        self._user_repository = UserRepository()

    def create_user(self) -> t.Dict[str, t.Any]:
        data = self._user_input_data.to_dict()
        self._user_repository.create(data)

        cmd_create_user = (
            f'useradd --no-create-home '
            f'--shell /bin/bash '
            f'--expiry {data["expiration_date"].split(" ")[0]} '
            f'{data["username"]}'
        )
        cmd_set_password = f'echo {data["username"]}:{data["password"]} | chpasswd'

        exec_command(cmd_create_user)
        exec_command(cmd_set_password)
        return data

    def update_password(self, password: str = None) -> t.Dict[str, t.Any]:
        password = password or self._user_input_data.password
        user = self._user_repository.get_by_username(self._user_input_data.username)

        user_dto = UserDto.of(user)
        user_dto.password = password
        self._user_repository.update(user.id, user_dto)

        cmd_set_password = f'echo {self._user_input_data.username}:{password} | chpasswd'
        exec_command(cmd_set_password)
        return user_dto.to_dict()

    def update_connection_limit(self, username: str, connection_limit: int) -> t.Dict[str, t.Any]:
        if isinstance(connection_limit, str) and not connection_limit.isdigit():
            raise ValueError('Limite de conexões deve conter apenas números')

        user = self._user_repository.get_by_username(username)

        user_dto = UserDto.of(user)
        user_dto.connection_limit = connection_limit
        self._user_repository.update(user.id, user_dto)
        return user_dto.to_dict()

    def update_expiration_date(self, username: str, expiration_date: str) -> t.Dict[str, t.Any]:
        if not expiration_date.isdigit() or len(expiration_date) != 10:
            raise ValueError('Data de expiração inválida')

        user = self._user_repository.get_by_username(username)

        user_dto = UserDto.of(user)
        user_dto.expiration_date = expiration_date
        self._user_repository.update(user.id, user_dto)

        expiration_date = expiration_date.split()[0]
        cmd_set_expiration_date = f'usermod --expiry {expiration_date} {username}'
        exec_command(cmd_set_expiration_date)
        return user_dto.to_dict()

    @staticmethod
    def show_message_user_created(user: t.Dict[str, t.Any]):
        line = create_menu_bg('Usuário criado com sucesso!')
        line += '\n'
        line += COLOR_NAME.YELLOW + 'Nome de usuário: ' + COLOR_NAME.RESET + user['username'] + '\n'
        line += COLOR_NAME.YELLOW + 'Senha: ' + COLOR_NAME.RESET + user['password'] + '\n'
        line += (
            COLOR_NAME.YELLOW
            + 'Limite de conexões: '
            + COLOR_NAME.RESET
            + user['connection_limit']
            + '\n'
        )
        line += (
            COLOR_NAME.YELLOW
            + 'Data de expiração: '
            + COLOR_NAME.RESET
            + user['expiration_date']
            + '\n'
        )

        print(line)


class UserMenu:
    def __init__(self, repository: UserRepository):
        self._repository = repository
        self._console = Console('SELECIONE UM USUÁRIO')
        self._user_selected = None

    @property
    def user_selected(self) -> t.Dict[str, t.Any]:
        return self._user_selected

    def _set_user_selected(self, user: t.Dict[str, t.Any]) -> None:
        if not user or not isinstance(user, dict):
            raise ValueError('Usuário não informado')

        self._user_selected = user
        self._console.exit()

    def _create_menu(self) -> None:
        self._console.items.clear()
        for user in self._repository.get_all():
            user_dto = UserDto.of(user)
            self._console.append_item(
                FuncItem(
                    user_dto['username'],
                    self._set_user_selected,
                    user_dto.to_dict(),
                )
            )

    def show(self) -> t.Dict[str, t.Any]:
        if self.user_selected is None:
            self._create_menu()
            self._console.show()

        return self.user_selected


def password_change_action(user_data: t.Dict[str, t.Any]) -> None:
    if not user_data:
        return

    logger.info('Usurário: %s', COLOR_NAME.YELLOW + user_data['username'] + COLOR_NAME.RESET)
    logger.info('Senha atual: %s', COLOR_NAME.YELLOW + user_data['password'] + COLOR_NAME.RESET)

    user_manager = UserManager(UserInputData.of(user_data))
    user_manager.update_password(UserInputData().password)
    logger.info('Senha alterada com sucesso!')


def limit_connection_change_action(user_data: t.Dict[str, t.Any]) -> None:
    if not user_data:
        return

    logger.info('Usurário: %s', COLOR_NAME.YELLOW + user_data['username'] + COLOR_NAME.RESET)
    logger.info(
        'Limite atual: %s',
        COLOR_NAME.YELLOW + str(user_data['connection_limit']) + COLOR_NAME.RESET,
    )

    user_manager = UserManager(UserInputData.of(user_data))
    user_manager.update_connection_limit(UserInputData().connection_limit)
    logger.info('Limite de conexões alterado com sucesso!')


def expiration_date_change_action(user_data: t.Dict[str, t.Any]) -> None:
    if not user_data:
        return

    logger.info('Usurário: %s', COLOR_NAME.YELLOW + user_data['username'] + COLOR_NAME.RESET)
    logger.info(
        'Data atual: %s', COLOR_NAME.YELLOW + user_data['expiration_date'] + COLOR_NAME.RESET
    )

    user_manager = UserManager(UserInputData.of(user_data))
    user_manager.update_expiration_date(UserInputData().expiration_date)
    logger.info('Data de expiração alterada com sucesso!')


console = Console('GERENCIADOR DE USUÁRIOS')
console.append_item(
    FuncItem(
        'CRIAR USUÁRIO',
        lambda: UserManager(UserInputData()).create_user(),
    )
)
console.append_item(
    FuncItem(
        'ALTERAR SENHA',
        lambda: password_change_action(UserMenu(UserRepository()).show()),
    )
)
console.append_item(
    FuncItem(
        'ALTERAR LIMITE',
        lambda: limit_connection_change_action(UserMenu(UserRepository()).show()),
    )
)
console.append_item(
    FuncItem(
        'ALTERAR EXPIRACAO',
        lambda: expiration_date_change_action(UserMenu(UserRepository()).show()),
    )
)
console.show()
