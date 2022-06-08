import os

from .install import openvpn_install, uninstall_openvpn, create_ovpn_client, OPENVPN_PATH


class OpenVPNManager:
    def __init__(self):
        pass

    @staticmethod
    def openvpn_is_installed() -> bool:
        status = OpenVPNManager.openvpn_is_running()

        if not status:
            status = os.path.exists(OPENVPN_PATH) and os.path.exists(
                os.path.join(OPENVPN_PATH, 'server.conf')
            )

        return status

    @staticmethod
    def openvpn_install() -> bool:
        try:
            openvpn_install()
            return OpenVPNManager.openvpn_is_installed()
        except (Exception, KeyboardInterrupt):
            return False

    @staticmethod
    def openvpn_uninstall() -> bool:
        uninstall_openvpn()

        return not OpenVPNManager.openvpn_is_installed()

    @staticmethod
    def create_ovpn_client(username: str) -> None:
        create_ovpn_client(username)

    @staticmethod
    def openvpn_is_running() -> bool:
        status = os.system('pgrep openvpn') == 0
        return status

    @staticmethod
    def openvpn_start() -> bool:
        os.system('systemctl start openvpn@server.service')
        return OpenVPNManager.openvpn_is_running()

    @staticmethod
    def openvpn_stop() -> bool:
        os.system('systemctl stop openvpn@server.service')
        return not OpenVPNManager.openvpn_is_running()

    @staticmethod
    def openvpn_restart() -> bool:
        os.system('systemctl restart openvpn@server.service')
        return OpenVPNManager.openvpn_is_running()

    @staticmethod
    def change_openvpn_port(port: int) -> None:
        with open(os.path.join(OPENVPN_PATH, 'server.conf'), 'r') as f:
            lines = f.readlines()

        with open(os.path.join(OPENVPN_PATH, 'server.conf'), 'w') as f:
            for line in lines:

                if 'port' in line:
                    line = 'port {}\n'.format(port)

                f.write(line)

    @staticmethod
    def get_current_port() -> int:
        with open(os.path.join(OPENVPN_PATH, 'server.conf'), 'r') as f:
            lines = f.readlines()

        for line in lines:
            if 'port' in line:
                port = int(line.split(' ')[1])
                return port
