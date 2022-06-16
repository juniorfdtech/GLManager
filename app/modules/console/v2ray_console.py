import typing as t

from console import Console, FuncItem, COLOR_NAME
from console.formatter import create_menu_bg, create_line

from app.utilities.logger import logger
from app.utilities.utils import get_ip_address

from app.data.repositories import UserRepository
from app.domain.use_cases import UserUseCase
from app.domain.dtos import UserDto

from .utils import ConsoleUUID, UserMenuConsole
from .v2ray_utils import V2RayManager


class V2RayActions:
    v2ray_manager = V2RayManager()

    @staticmethod
    def install(callback: t.Callable) -> None:
        logger.info('Instalando V2Ray...')
        status = V2RayActions.v2ray_manager.install()

        if status:
            logger.info('Gere um novo UUID para o cliente.')
            logger.info('V2Ray instalado com sucesso!')
        else:
            logger.error('Falha ao instalar V2Ray!')

        Console.pause()
        callback()

    @staticmethod
    def uninstall(callback: t.Callable) -> None:
        logger.info('Desinstalando V2Ray...')
        status = V2RayActions.v2ray_manager.uninstall()

        if status:
            logger.info('V2Ray desinstalado com sucesso!')
        else:
            logger.error('Falha ao desinstalar V2Ray!')

        Console.pause()
        callback()

    @staticmethod
    def start(callback: t.Callable) -> None:
        logger.info('Iniciando V2Ray...')
        status = V2RayActions.v2ray_manager.start()

        if status:
            logger.info('V2Ray iniciado com sucesso!')
        else:
            logger.error('Falha ao iniciar V2Ray!')

        Console.pause()
        callback()

    @staticmethod
    def stop(callback: t.Callable) -> None:
        logger.info('Parando V2Ray...')
        status = V2RayActions.v2ray_manager.stop()

        if status:
            logger.info('V2Ray parado com sucesso!')
        else:
            logger.error('Falha ao parar V2Ray!')

        Console.pause()
        callback()

    @staticmethod
    def restart(callback: t.Callable) -> None:
        logger.info('Reiniciando V2Ray...')
        status = V2RayActions.v2ray_manager.restart()

        if status:
            logger.info('V2Ray reiniciado com sucesso!')
        else:
            logger.error('Falha ao reiniciar V2Ray!')

        Console.pause()
        callback()

    @staticmethod
    def change_port() -> None:
        v2ray_manager = V2RayActions.v2ray_manager

        current_port = v2ray_manager.get_running_port()
        logger.info('Porta atual: %s' % current_port)

        try:
            port = None
            while port is None:
                port = input(COLOR_NAME.YELLOW + 'Porta: ' + COLOR_NAME.RESET)

                try:
                    if not port.isdigit() or int(port) < 1 or int(port) > 65535:
                        raise ValueError

                    port = int(port)
                    if port == v2ray_manager.get_running_port():
                        logger.error('Porta já em uso!')
                        port = None

                except ValueError:
                    logger.error('Porta inválida!')
                    port = None

            if v2ray_manager.change_port(port):
                logger.info('Porta alterada para %s' % port)
            else:
                logger.error('Falha ao alterar porta!')

        except KeyboardInterrupt:
            return

        Console.pause()

    @staticmethod
    def create_uuid() -> None:
        v2ray_manager = V2RayActions.v2ray_manager
        uuid = v2ray_manager.create_new_uuid()
        logger.info('UUID criado: %s' % uuid)

        result = input(
            COLOR_NAME.YELLOW + 'Deseja associar este UUID ao usuário? (s/n): ' + COLOR_NAME.RESET
        )
        if result.lower() == 's':
            user_use_case = UserUseCase(UserRepository())

            console = UserMenuConsole(user_use_case)
            console.start()

            user_selected = console.user_selected

            if user_selected is not None:
                user_dto = UserDto.of(user_selected)
                user_dto.v2ray_uuid = uuid

                user_use_case.update(user_dto)
                message = COLOR_NAME.YELLOW + 'Usuário: %s' % user_dto.username + COLOR_NAME.RESET
                message += '\n' + COLOR_NAME.YELLOW + 'UUID: %s' % uuid + COLOR_NAME.RESET
                print(message)

                logger.info('UUID associado com sucesso!')
                Console.pause()

    @staticmethod
    def remove_uuid(uuid: str = None) -> None:
        if uuid is None:
            return

        v2ray_manager = V2RayActions.v2ray_manager
        uuid_list = v2ray_manager.get_uuid_list()

        if uuid not in uuid_list:
            logger.error('UUID não encontrado!')
            return

        v2ray_manager.remove_uuid(uuid)

        user_use_case = UserUseCase(UserRepository())
        user_dto = user_use_case.get_by_uuid(uuid)

        if user_dto:
            user_dto.v2ray_uuid = None
            user_use_case.update(user_dto)

        logger.info('UUID removido: %s' % uuid)

        Console.pause()

    @staticmethod
    def view_vless_config() -> None:
        vless_base_link = 'vless://@{}:{}?encryption={}&type={}#{}'

        ip_address = get_ip_address()
        port = V2RayActions.v2ray_manager.get_running_port()

        config = V2RayActions.v2ray_manager.config.load()
        type = config['inbounds'][0]['streamSettings']['network']
        encryption = config['inbounds'][0]['streamSettings'].get('security')
        protocol = config['inbounds'][0]['protocol']

        vless_link = vless_base_link.format(
            ip_address,
            port,
            encryption,
            type,
            '%s:%d' % (ip_address, port),
        )

        Console.clear_screen()
        print(create_line(show=False))
        print(COLOR_NAME.YELLOW + 'V2Ray Config' + COLOR_NAME.RESET)
        print(COLOR_NAME.GREEN + 'IP: %s' % ip_address + COLOR_NAME.RESET)
        print(COLOR_NAME.GREEN + 'Port: %s' % port + COLOR_NAME.RESET)
        print(COLOR_NAME.GREEN + 'Protocol: %s' % protocol + COLOR_NAME.RESET)
        print(COLOR_NAME.GREEN + 'Type: %s' % type + COLOR_NAME.RESET)
        print(create_line(show=False))

        print(COLOR_NAME.YELLOW + 'V2Ray Link' + COLOR_NAME.RESET)
        print(COLOR_NAME.GREEN + 'Link: %s' % vless_link + COLOR_NAME.RESET)
        print(create_line(show=False))

        Console.pause()


class ConsoleDeleteUUID(ConsoleUUID):
    def __init__(self, v2ray_manager: V2RayManager, user_use_case: UserUseCase = None):
        super().__init__('Remover UUID', v2ray_manager, user_use_case)

    def select_uuid(self, uuid: str) -> None:
        V2RayActions.remove_uuid(uuid)

        self.console.items.clear()
        self.create_items()


class ConsoleListUUID(ConsoleUUID):
    def __init__(self, v2ray_manager: V2RayManager, user_use_case: UserUseCase = None):
        super().__init__('Listar UUIDs', v2ray_manager, user_use_case)

    def start(self) -> None:
        self.create_items()

        if len(self.console.items) > 1:
            del self.console.items[-1]

        self.console.clear_screen()
        self.console.print_items()
        self.console.pause()


def v2ray_console_main():
    console = Console('V2Ray Manager')
    action = V2RayActions()

    if not action.v2ray_manager.is_installed():
        console.append_item(
            FuncItem(
                'INSTALAR V2RAY',
                action.install,
                v2ray_console_main,
                shuld_exit=True,
            )
        )
        console.show()
        return

    if not V2RayManager.is_running():
        console.append_item(
            FuncItem(
                'INICIAR V2RAY',
                action.start,
                v2ray_console_main,
                shuld_exit=True,
            )
        )

    if V2RayManager.is_running():
        console.append_item(
            FuncItem(
                'PARAR V2RAY',
                action.stop,
                v2ray_console_main,
                shuld_exit=True,
            )
        )
        console.append_item(
            FuncItem(
                'REINICIAR V2RAY',
                action.restart,
                v2ray_console_main,
                shuld_exit=True,
            )
        )

    console.append_item(FuncItem('ALTERAR PORTA', action.change_port))
    console.append_item(FuncItem('CRIAR NOVO UUID', action.create_uuid))
    console.append_item(
        FuncItem(
            'REMOVER UUID',
            lambda: ConsoleDeleteUUID(action.v2ray_manager, UserUseCase(UserRepository)).start(),
        )
    )
    console.append_item(
        FuncItem(
            'LISTAR UUID\'S',
            lambda: ConsoleListUUID(action.v2ray_manager, UserUseCase(UserRepository)).start(),
        )
    )
    console.append_item(FuncItem('VER CONFIG. V2RAY', action.view_vless_config))
    console.append_item(
        FuncItem(
            'DESINSTALAR V2RAY',
            action.uninstall,
            v2ray_console_main,
            shuld_exit=True,
        )
    )
    console.show()
