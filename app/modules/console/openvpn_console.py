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

    @staticmethod
    def uninstall(callback: t.Callable) -> None:
        logger.info('Desinstalando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_uninstall()

        if status:
            logger.info('OpenVPN desinstalado com sucesso!')
        else:
            logger.error('Falha ao desinstalar OpenVPN!')

        Console.pause()
        callback(status)

    @staticmethod
    def start(callback: t.Callable) -> None:
        logger.info('Iniciando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_start()

        if status:
            logger.info('OpenVPN iniciado com sucesso!')
        else:
            logger.error('Falha ao iniciar OpenVPN!')

        Console.pause()
        callback(status)

    @staticmethod
    def stop(callback: t.Callable) -> None:
        logger.info('Parando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_stop()

        if status:
            logger.info('OpenVPN parado com sucesso!')
        else:
            logger.error('Falha ao parar OpenVPN!')

        Console.pause()
        callback(status)

    @staticmethod
    def restart(callback: t.Callable) -> None:
        logger.info('Reiniciando OpenVPN...')
        status = OpenVPNActions.openvpn_manager.openvpn_restart()

        if status:
            logger.info('OpenVPN reiniciado com sucesso!')
        else:
            logger.error('Falha ao reiniciar OpenVPN!')

        Console.pause()
        callback(status)

    @staticmethod
    def change_port():
        current_port = OpenVPNActions.openvpn_manager.get_current_port()
        logger.info('Porta atual: {}'.format(current_port))

        port = None
        while not port:
            port = input('Porta: ')

            try:
                port = int(port)
                if port < 1 or port > 65535:
                    raise ValueError
            except ValueError:
                logger.error('Porta inválida!')
                port = None

        OpenVPNActions.openvpn_manager.change_openvpn_port(port)
        OpenVPNActions.openvpn_manager.openvpn_restart()
        logger.info('Porta alterada para {}!'.format(port))
        Console.pause()


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

    if OpenVPNManager.openvpn_is_running():
        console.append_item(
            FuncItem(
                'PARAR OPENVPN',
                func=lambda: OpenVPNActions.stop(console_callback),
            )
        )
    else:
        console.append_item(
            FuncItem(
                'INICIAR OPENVPN',
                func=lambda: OpenVPNActions.start(console_callback),
            )
        )
    console.append_item(
        FuncItem(
            'REINICIAR OPENVPN',
            func=lambda: OpenVPNActions.restart(console_callback),
        )
    )
    console.append_item(
        FuncItem(
            'ALTERAR PORTA',
            func=lambda: OpenVPNActions.change_port(),
        )
    )

    console.append_item(
        FuncItem(
            'DESINSTALAR OPENVPN',
            func=lambda: OpenVPNActions.uninstall(console_callback),
        )
    )
    console.show()