import os

from .install import (
    EASYRSA_PATH,
    EASYRSA_PKI_CA,
    EASYRSA_PKI_CERT_PATH,
    EASYRSA_PKI_KEY_PATH,
    CLIENT_COMMON_CONFIG,
    EASYRSA_PKI_TLS,
    ROOT_PATH,
    OPENVPN_PATH,
)


def create_ovpn_client(username: str) -> str:
    os.chdir(EASYRSA_PATH)
    os.system('./easyrsa build-client-full %s nopass 1>/dev/null' % username)

    ovpn_config_template = '\n'.join(
        [
            '%s',
            '<ca>',
            '%s',
            '</ca>',
            '<cert>',
            '%s',
            '</cert>',
            '<key>',
            '%s',
            '</key>',
            '<tls-auth>',
            '%s',
            '</tls-auth>',
        ]
    )

    ovpn_config = ovpn_config_template % (
        open(CLIENT_COMMON_CONFIG).read().strip(),
        open(EASYRSA_PKI_CA).read().strip(),
        open(EASYRSA_PKI_CERT_PATH + username + '.crt').read().strip(),
        open(EASYRSA_PKI_KEY_PATH + username + '.key').read().strip(),
        open(EASYRSA_PKI_TLS).read().strip(),
    )

    path = os.path.join(ROOT_PATH, username + '.ovpn')

    with open(path, 'w') as f:
        f.write(ovpn_config)

    return path


class OpenVPNUtils:
    @staticmethod
    def openvpn_is_running() -> bool:
        status = os.system('pgrep openvpn') == 0
        return status

    @staticmethod
    def openvpn_is_installed() -> bool:
        status = OpenVPNUtils.openvpn_is_running()

        if not status:
            status = os.path.exists(OPENVPN_PATH) and os.path.exists(
                os.path.join(OPENVPN_PATH, 'server.conf')
            )

        return status

    @staticmethod
    def create_ovpn_client(username: str) -> str:
        return create_ovpn_client(username)
