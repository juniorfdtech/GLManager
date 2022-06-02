import typing as t

from console import Console, FuncItem, Formatter

from app.domain.dtos import UserDto
from app.domain.use_cases import UserUseCase
from app.utilities.logger import logger
from .v2ray_utils import V2RayManager


class UserMenuConsole:
    def __init__(
        self,
        user_use_case: UserUseCase,
        title: str = 'SELECIONE UM USUÁRIO',
    ):
        self._user_use_case = user_use_case
        self._console = Console(title)
        self._user_selected = None

    @property
    def user_selected(self) -> t.Dict[str, t.Any]:
        return self._user_selected

    @property
    def _users(self) -> t.List[UserDto]:
        return self._user_use_case.get_all()

    def select_user(self, user: t.Dict[str, t.Any]) -> None:
        if not user or not isinstance(user, dict):
            raise ValueError('Usuário não informado')

        self._user_selected = user
        self._console.exit()

    def create_items(self) -> None:
        self._console.items.clear()

        if not self._users:
            logger.error('Nenhum usuario foi encontrado.')
            self._console.pause()
            return

        for user in self._users:
            user_dto = UserDto.of(user)
            self._console.append_item(
                FuncItem(
                    user['username'],
                    self.select_user,
                    user_dto.to_dict(),
                )
            )

    def width(self) -> int:
        width = [len(user['username']) for user in self._users]
        return max(width)

    def show(self) -> t.Union[t.Dict[str, t.Any], t.Dict[str, t.Any]]:
        if self.user_selected is None:
            self.create_items()
            self._console.show()

        return self.user_selected


class ConsoleUUID:
    def __init__(self, title: str = 'V2Ray UUID', v2ray_manager: V2RayManager = None) -> None:
        self.title = title
        self.console = Console(title=self.title, formatter=Formatter(1))
        self.v2ray_manager = v2ray_manager

    def select_uuid(self, uuid: str) -> None:
        raise NotImplementedError

    def create_items(self) -> None:
        uuids = self.v2ray_manager.get_uuid_list()
        if not uuids:
            logger.error('Nenhum UUID encontrado')
            Console.pause()
            return

        for uuid in uuids:
            self.console.append_item(FuncItem(uuid, self.select_uuid, uuid))

    def start(self) -> None:
        self.create_items()
        self.console.show()