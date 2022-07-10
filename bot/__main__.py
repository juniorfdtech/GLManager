import argparse

from bot.bot_config import set_admin_id, set_bot_token, get_admin_id, get_bot_token

parser = argparse.ArgumentParser(description='Helper for the bot')
parser.add_argument('--set-token', dest='token', help='Set the bot token')
parser.add_argument('--set-admin', dest='admin', help='Set the admin id')

parser.add_argument('--get-token', dest='get_token', action='store_true', help='Get the bot token')
parser.add_argument('--get-admin', dest='get_admin', action='store_true', help='Get the admin id')

parser.add_argument(
    '--delete-token',
    dest='delete_token',
    action='store_true',
    help='Delete the bot token',
)
parser.add_argument(
    '--delete-admin',
    dest='delete_admin',
    action='store_true',
    help='Delete the admin id',
)

parser.add_argument(
    '--edit-config',
    dest='edit_config',
    action='store_true',
    help='Edit the config file',
)

parser.add_argument('--start', dest='start', action='store_true', help='Start the bot')
parser.add_argument('--stop', dest='stop', action='store_true', help='Stop the bot')
parser.add_argument(
    '--daemon', dest='daemon', action='store_true', help='Run the bot as a daemon (Linux only)'
)
parser.add_argument(
    '--pidfile', dest='pidfile', help='Set the pid file (Linux only)', default='/tmp/bot.pid'
)

args = parser.parse_args()


def execute():
    import bot.commands
    from bot.bot import bot

    bot.infinity_polling()


def main():
    args = parser.parse_args()

    if args.token:
        set_bot_token(args.token)

    if args.admin:
        set_admin_id(args.admin)

    if args.get_token:
        print(get_bot_token())

    if args.get_admin:
        print(get_admin_id())

    if args.delete_token:
        set_bot_token('')

    if args.delete_admin:
        set_admin_id('')

    if args.edit_config:
        import os

        os.system('nano /etc/GLManager/config.json')

    if args.start:
        if args.daemon:
            from .daemon import Daemon

            class BotDaemon(Daemon):
                def __init__(self):
                    super().__init__(pidfile=args.pidfile)

                def run(self):
                    execute()

            daemon = BotDaemon()
            daemon.start()
            return

        execute()

    if args.stop:
        from .daemon import Daemon

        daemon = Daemon(pidfile=args.pidfile)
        daemon.stop()
        return


if __name__ == '__main__':
    main()
