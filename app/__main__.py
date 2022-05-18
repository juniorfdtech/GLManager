import sys

from app.modules.cli import user_cli_main
from app.modules.console import main_console

if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_cli_main(sys.argv[1:])
    else:
        main_console()
