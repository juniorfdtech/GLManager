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


class SocksManager:
    def is_running(self, port: int = 80) -> bool:
        cmd = 'screen -ls | grep %s' % port
        return os.system(cmd) == 0

    def start(self, mode: str = 'http', src_port: int = 80, dst_port: int = 8080) -> None:
        cmd = 'screen -mdS socks:%s:%s python3 %s --port %s --remote 127.0.0.1:%s --%s' % (
            src_port,
            mode,
            SOCKS_PATH,
            src_port,
            dst_port,
            mode,
        )

        if mode == 'https':
            cmd += ' --cert %s' % CERT_PATH

        return os.system(cmd) == 0

    def stop(self, mode: str = 'http', src_port: int = 80) -> None:
        cmd = 'screen -X -S socks:%s:%s quit' % (src_port, mode)
        return os.system(cmd) == 0

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

    @staticmethod
    def get_src_and_dst_ports() -> t.Tuple[str, int, int]:
        cmd = 'ps -ef | grep python3 | grep socks | grep -v grep'
        output = os.popen(cmd).read().strip()
        result = []

        for line in output.split('\n'):
            if not line:
                continue

            src_port = int(line.split('--port')[1].split()[0])
            dst_port = int(line.split('--remote')[1].split()[0].split(':')[1])

            mode = 'null'

            if 'http' in line:
                mode = 'http'

            if 'https' in line:
                mode = 'https'

            data = (mode, src_port, dst_port)

            if data not in result:
                result.append(data)

        return result


class ConsolePort:
    def __init__(self, title: str = 'SELECIONE UMA PORTA') -> None:
        self._title = title
        self._console = Console(title)
        self._current_port_selected = None
        self._current_mode_selected = None

    @property
    def current_port_selected(self) -> int:
        if self._current_port_selected is None:
            self._current_port_selected = self.show()

        return self._current_port_selected

    @property
    def current_mode_selected(self) -> str:
        if self._current_mode_selected is None:
            self.show()

        return self._current_mode_selected

    def _set_port_mode_selected(self, port: int, mode: str) -> None:
        self._current_port_selected = port
        self._current_mode_selected = mode
        self._console.exit()

    def _create_menu(self) -> None:
        self._console.items.clear()

        socks = SocksManager.get_running_socks()

        if not socks:
            logger.error('Nenhuma porta ativa')
            return

        width = self.width([i for x in socks.items() for i in x])
        for port, mode in socks.items():
            item = FuncItem(
                '%s - %s' % (str(port).ljust(width), mode),
                self._set_port_mode_selected,
                str(port),
                mode,
            )
            self._console.items.append(item)

        self._console.items.append(FuncItem('Sair', self._console.exit))

    def width(self, ports: t.List[t.Any]) -> int:
        return max(len(str(port)) for port in ports)

    def show(self) -> int:
        if self._current_port_selected is None:
            self._create_menu()
            self._console.show()

        return self._current_port_selected


class FormatterSocks(Formatter):
    def build_menu(self, title):
        menu = super().build_menu(title)
        running_ports = SocksManager.get_src_and_dst_ports()

        if not running_ports:
            return menu

        for mode, src_port, dst_port in running_ports:
            menu += '%s %s %s\n' % (
                COLOR_NAME.GREEN + mode + COLOR_NAME.END,
                COLOR_NAME.GREEN + str(src_port).rjust(21) + COLOR_NAME.END,
                COLOR_NAME.GREEN + str(dst_port).rjust(22) + COLOR_NAME.END,
            )

        return menu + create_line(color=COLOR_NAME.BLUE, show=False) + '\n'


class ConsoleStopPort(ConsolePort):
    def _set_port_mode_selected(self, port: int, mode: str) -> None:
        manager = SocksManager()

        if manager.stop(mode, port):
            logger.info('Porta %s desligada' % port)
            self._create_menu()
        else:
            logger.error('Erro ao desligar porta %s' % port)

        self._current_mode_selected = mode
        self._current_port_selected = port

        self._console.pause()


class SocksActions:
    @staticmethod
    def start(mode: str = 'http') -> None:
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

        while True:
            try:
                dst_port = input(COLOR_NAME.YELLOW + 'Porta de destino: ' + COLOR_NAME.RESET)
                dst_port = int(dst_port)

                if dst_port == src_port:
                    raise ValueError

                break
            except ValueError:
                logger.error('Porta inválida!')

            except KeyboardInterrupt:
                return

        if src_port <= 0 or dst_port <= 0:
            logger.error('Porta inválida!')
            Console.pause()
            return

        if manager.is_running(src_port):
            logger.error('Porta %s já está em uso!' % src_port)
            Console.pause()
            return

        if not manager.start(src_port=src_port, dst_port=dst_port, mode=mode):
            logger.error('Falha ao iniciar proxy!')
            Console.pause()
            return

        logger.info('Proxy iniciado com sucesso!')
        Console.pause()

    @staticmethod
    def stop() -> None:
        console = ConsoleStopPort()
        console.show()

    @staticmethod
    def create_message_running_ports(running_ports: t.List[int]) -> str:
        message = create_line(show=False) + '\n'
        message += COLOR_NAME.YELLOW + 'Em uso: ' + COLOR_NAME.RESET
        message += ', '.join(str(port) for port in running_ports)
        message += '\n'
        message += create_line(show=False)

        return message


def socks_console_main():
    process_install_screen()

    console = Console('SOCKS Manager', formatter=FormatterSocks())
    console.append_item(FuncItem('ABRIR PORTA HTTP', SocksActions.start, 'http'))
    console.append_item(FuncItem('ABRIR PORTA HTTPS', SocksActions.start, 'https'))
    console.append_item(FuncItem('FECHAR PORTA', SocksActions.stop))
    console.show()
