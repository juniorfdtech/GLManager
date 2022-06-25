import typing as t
import os

from console import Console, FuncItem, COLOR_NAME
from console.formatter import create_menu_bg, create_line, Formatter

from scripts import SOCKS_PATH, CERT_PATH

from app.utilities.logger import logger


def check_screen_is_installed():
    command = 'command -v screen >/dev/null 2>&1'
    return os.system(command) == 0


def process_install_screen():
    if check_screen_is_installed():
        return

    answer = input(
        COLOR_NAME.YELLOW + 'Screen não está instalado. Deseja instalar? [s/N]: ' + COLOR_NAME.END
    )
    if answer.lower() == 's':
        logger.info('Instalando screen...')
        os.system('sudo apt-get install screen -y >/dev/null 2>&1')
        logger.info('Screen instalado com sucesso!')
        Console.pause()


class Flag:
    def __init__(self, name: str, port: int = None):
        self.__name = name
        self.__port = port

        if self.__port is None and self.__name is not None:
            port = self.current_flag(self.__name)

            if port:
                self.__port = int(port)

    @property
    def name(self) -> str:
        if self.__name is None:
            raise ValueError('Name is not set')

        return self.__name

    @name.setter
    def name(self, value: str):
        if value is None:
            raise ValueError('Name is not set')

        self.__name = value

    @property
    def port(self) -> int:
        if self.__port == -1:
            raise ValueError('Port is not set')

        return self.__port

    @port.setter
    def port(self, port: int):
        if not isinstance(port, int):
            raise TypeError('Port must be an integer')

        if port < 0 or port > 65535:
            raise ValueError('Port must be between 0 and 65535')

        self.__port = port

    @property
    def value(self):
        flag = self.name

        if not flag.startswith('--'):
            flag = '--' + flag

        flag += ' ' + str(self.port)

        return flag

    @staticmethod
    def current_flag(flag_name: str) -> str:
        flag_name_parsed = flag_name
        if '-' in flag_name:
            flag_name_parsed = '\-'.join(flag_name.split('-'))

        command = 'ps -aux | grep -i ' + flag_name_parsed + ' | grep -v grep'
        output = os.popen(command).read().strip()

        for line in output.split('\n'):
            data = line.split(flag_name)
            if len(data) > 1:
                return data[1].split()[0]

        return ''


class OpenVpnFlag(Flag):
    def __init__(self):
        super().__init__('openvpn-port')
        if not self.port:
            self.port = 1194


class SSHFlag(Flag):
    def __init__(self):
        super().__init__('ssh-port')
        if not self.port:
            self.port = 22


class V2rayFlag(Flag):
    def __init__(self):
        super().__init__('v2ray-port')
        if not self.port:
            self.port = 1080


class FlagUtils:
    def __init__(self):
        self.__openvpn_flag = OpenVpnFlag()
        self.__ssh_flag = SSHFlag()
        self.__v2ray_flag = V2rayFlag()

        self.__flags: t.List[Flag] = [
            self.__openvpn_flag,
            self.__ssh_flag,
            self.__v2ray_flag,
        ]

    def set_flag(self, flag: Flag):
        for f in self.__flags:
            if f.name == flag.name:
                f.port = flag.port

    def command(self) -> str:
        return '%s %s %s' % (
            self.__openvpn_flag.value,
            self.__ssh_flag.value,
            self.__v2ray_flag.value,
        )

    def values(self) -> t.List[str]:
        return [
            self.__openvpn_flag.value,
            self.__ssh_flag.value,
            self.__v2ray_flag.value,
        ]


class SocksManager:
    @staticmethod
    def is_running(mode: str = 'http') -> bool:
        cmd = 'screen -ls | grep -i "socks:[0-9]*:%s\\b"' % mode
        return os.system(cmd) == 0

    def start(self, mode: str = 'http', src_port: int = 80, flag_utils: FlagUtils = None):
        cmd = 'screen -mdS socks:%s:%s python3 %s --port %s %s --%s' % (
            src_port,
            mode,
            SOCKS_PATH,
            src_port,
            flag_utils.command(),
            mode,
        )

        if mode == 'https':
            cmd += ' --cert %s' % CERT_PATH

        return os.system(cmd) == 0 and self.is_running(mode)

    def stop(self, mode: str = 'http', src_port: int = 80) -> None:
        cmd = 'screen -X -S socks:%s:%s quit' % (src_port, mode)
        return os.system(cmd) == 0

    @staticmethod
    def get_running_port(mode: str = 'http') -> int:
        cmd = 'screen -ls | grep -ie "socks:[0-9]*:%s\\b"' % mode
        output = os.popen(cmd).read().strip()

        for line in output.split('\n'):
            data = line.split(':')
            if len(data) > 1:
                return int(data[1].split(' ')[0])

        return 0

    @staticmethod
    def get_running_ports() -> t.List[int]:
        cmd = 'screen -ls | grep socks: | awk \'{print $1}\' | awk -F: \'{print $2}\''
        output = os.popen(cmd).read()
        return [int(port) for port in output.split('\n') if port]

    @staticmethod
    def get_running_socks() -> t.Dict[int, str]:
        cmd = 'screen -ls | grep socks: | awk \'{print $1}\''
        output = os.popen(cmd).readlines()
        socks = dict(
            (int(port), mode.strip()) for port, mode in (line.split(':')[1:] for line in output)
        )
        return socks


class ConsoleMode:
    def __init__(self):
        self.console = Console('SELECIONE O MODO DE CONEXAO')
        self.console.append_item(FuncItem('HTTP', lambda: 'http', exit_on_select=True))
        self.console.append_item(FuncItem('HTTPS', lambda: 'https', exit_on_select=True))

    def start(self) -> str:
        self.console.show()
        return self.console.item_returned

    @classmethod
    def get_mode(cls) -> str:
        return cls().start()


class FormatterSocks(Formatter):
    def __init__(self, port: int, mode: str) -> None:
        super().__init__()
        self.port = port
        self.mode = mode

    def build_menu(self, title):
        menu = super().build_menu(title)

        if self.port <= 0:
            return menu

        flag_utils = FlagUtils()
        values = []

        for flag in flag_utils.values():
            name, port = flag.split()
            name = name.replace('--', '')
            name = name.split('-')[0]
            values.append(name + ' ' + str(port))

        for value in values:
            menu += '%s <-> %s <-> %s\n' % (
                COLOR_NAME.GREEN + self.mode.ljust(10) + COLOR_NAME.END,
                COLOR_NAME.GREEN + str(self.port).rjust(10).ljust(15) + COLOR_NAME.END,
                COLOR_NAME.GREEN + str(value).rjust(15) + COLOR_NAME.END,
            )

        return menu + create_line(color=COLOR_NAME.BLUE, show=False) + '\n'


class SocksActions:
    @staticmethod
    def start(mode: str, callback: t.Callable[[], None] = None) -> None:
        print(create_menu_bg('PORTA - ' + mode.upper()))

        manager = SocksManager()
        ports = manager.get_running_ports()

        if ports:
            print(SocksActions.create_message_running_ports(ports))

        while True:
            try:
                src_port = input(COLOR_NAME.YELLOW + 'Porta de escuta: ' + COLOR_NAME.RESET)
                src_port = int(src_port)

                if SocksManager().is_running(src_port):
                    logger.error('Porta %s já está em uso' % src_port)
                    continue

                break
            except ValueError:
                logger.error('Porta inválida!')

            except KeyboardInterrupt:
                return

        if not manager.start(mode=mode, src_port=src_port, flag_utils=FlagUtils()):
            logger.error('Falha ao iniciar proxy!')
            Console.pause()
            return

        logger.info('Proxy iniciado com sucesso!')
        Console.pause()

        if callback:
            callback()

    @staticmethod
    def stop(mode: str, port: int, callback: t.Callable[[], None] = None) -> None:
        manager = SocksManager()

        if not manager.stop(mode, port):
            logger.error('Falha ao desligar proxy!')
            Console.pause()
            return

        logger.info('Proxy desligado com sucesso!')
        Console.pause()

        if callback:
            callback(mode)

    @staticmethod
    def change_port(mode: str, flag: Flag) -> None:
        flag_utils = FlagUtils()
        socks_manager = SocksManager()
        current_port = flag.port

        logger.info('Porta atual: %s' % current_port)

        while True:
            try:
                new_port = input(COLOR_NAME.YELLOW + 'Nova porta: ' + COLOR_NAME.RESET)
                new_port = int(new_port)

                if new_port == current_port:
                    raise ValueError

                flag.port = new_port

                break
            except ValueError:
                logger.error('Porta inválida!')

            except KeyboardInterrupt:
                return

        running_port = socks_manager.get_running_port(mode)

        socks_manager.stop(mode, running_port)
        flag_utils.set_flag(flag)

        if not socks_manager.start(mode=mode, src_port=running_port, flag_utils=flag_utils):
            logger.error('Falha ao iniciar proxy!')
            Console.pause()
            return

        logger.info('Porta OpenVPN alterada com sucesso!')
        Console.pause()

    @staticmethod
    def create_message_running_ports(running_ports: t.List[int]) -> str:
        message = create_line(show=False) + '\n'
        message += COLOR_NAME.YELLOW + 'Em uso: ' + COLOR_NAME.RESET
        message += ', '.join(str(port) for port in running_ports)
        message += '\n'
        message += create_line(show=False)

        return message


def socks_console_main(mode: str):
    process_install_screen()

    running_port = SocksManager().get_running_port(mode)

    console = Console('SOCKS Manager ' + mode.upper(), formatter=FormatterSocks(running_port, mode))
    if not SocksManager.is_running(mode):
        console.append_item(
            FuncItem(
                'INICIAR',
                SocksActions.start,
                mode,
                lambda: socks_console_main(mode),
                shuld_exit=True,
            )
        )
        console.show()
        return

    console.append_item(
        FuncItem(
            'ALTERAR PORTA OPENVPN',
            SocksActions.change_port,
            mode,
            OpenVpnFlag(),
        )
    )
    console.append_item(
        FuncItem(
            'ALTERAR PORTA SSH',
            SocksActions.change_port,
            mode,
            SSHFlag(),
        )
    )
    console.append_item(
        FuncItem(
            'ALTERAR PORTA V2RAY',
            SocksActions.change_port,
            mode,
            V2rayFlag(),
        )
    )
    console.append_item(
        FuncItem(
            'PARAR',
            SocksActions.stop,
            mode,
            running_port,
            socks_console_main,
            shuld_exit=True,
        )
    )
    console.show()
