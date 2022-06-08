import os

from .install import openvpn_install, create_ovpn_client, OPENVPN_PATH


class OpenVPNManager:
    def __init__(self):
        pass

    @staticmethod
    def openvpn_install() -> None:
        openvpn_install()

    @staticmethod
    def create_ovpn_client(username: str) -> None:
        create_ovpn_client(username)

    @staticmethod
    def openvpn_is_installed() -> bool:
        status = os.path.exists(OPENVPN_PATH) and os.path.exists(
            os.path.join(OPENVPN_PATH, 'server.conf')
        )
        return status

    @staticmethod
    def openvpn_is_running() -> bool:
        pass
