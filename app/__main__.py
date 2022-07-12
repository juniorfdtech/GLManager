import sys

from console import Console, FuncItem
from app.modules.cli import user_cli_main
from app.modules.console import (
    user_console_main,
    socks_console_main,
    badvpn_console_main,
    v2ray_console_main,
    openvpn_console_main,
    tools_console_main,
)
from app.utilities.logger import logger


from app.domain.entities import *
from app.data.config import Base, DBConnection

with DBConnection() as db:
    Base.metadata.create_all(db.engine)


def connection_choices():
    console = Console('GERENCIADOR DE CONEXÕES')
    console.append_item(FuncItem('SOCKS HTTP', socks_console_main, 'http'))
    console.append_item(FuncItem('SOCKS SSL', socks_console_main, 'https'))
    console.append_item(FuncItem('OPENVPN', openvpn_console_main))
    console.append_item(FuncItem('V2RAY', v2ray_console_main))
    console.append_item(FuncItem('BADUDP', badvpn_console_main))

    console.show()


def main_cli():
    user_cli_main(sys.argv[1:])


def main_console():
    console = Console('GERENCIADOR')
    console.append_item(FuncItem('GERENCIADOR DE USUÁRIOS', user_console_main))
    console.append_item(FuncItem('GERENCIADOR DE CONEXÕES', connection_choices))
    console.append_item(FuncItem('GERENCIADOR DE FERRAMENTS', tools_console_main))
    console.append_item(FuncItem('GERENCIADOR DO PAINEL', input))

    try:
        console.show()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Até mais!')


def main():
    if len(sys.argv) > 1:
        main_cli()
    else:
        main_console()


if __name__ == '__main__':
    main()
