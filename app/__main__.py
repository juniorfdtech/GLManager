import sys

from app.modules.cli import user_cli_main
from app.modules.console import user_console_main, socks_console_main

from console import Console, FuncItem


def main_console_main():
    console = Console('GERENCIADOR')
    console.append_item(FuncItem('GERENCIADOR DE USUÁRIOS', user_console_main))
    console.append_item(FuncItem('GERENCIADOR DE CONEXÕES', socks_console_main))
    console.append_item(FuncItem('GERENCIADOR DO PAINEL', input))
    console.show()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_cli_main(sys.argv[1:])
    else:
        main_console_main()
    