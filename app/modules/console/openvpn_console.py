import typing as t

from console import Console, FuncItem, COLOR_NAME
from console.formatter import create_menu_bg, create_line

from app.utilities.logger import logger
from app.utilities.utils import get_ip

from app.data.repositories import UserRepository
from app.domain.use_cases import UserUseCase
from app.domain.dtos import UserDto

from .openvpn_utils import OpenVPNManager


class OpenVPNActions:
    openvpn_manager = OpenVPNManager()

    @staticmethod
    def install(callback: t.Callable) -> None:
        logger.info('Instalando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_install()

        if status:
            logger.info('OpenVPN instalado com sucesso!')
        else:
            logger.error('Falha ao instalar OpenVPN!')

        Console.pause()
        callback(status)


def openvpn_console_main() -> None:
    console = Console('OPENVPN Console')

    def console_callback(is_restart) -> None:
        if is_restart:
            console.exit()
            openvpn_console_main()

    if not OpenVPNManager.openvpn_is_installed():
        console.append_item(
            FuncItem(
                'INSTALAR OPENVPN',
                func=lambda: OpenVPNActions.install(console_callback),
            )
        )
        console.show()
        return
