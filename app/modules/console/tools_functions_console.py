import typing as t
import os
import tarfile
import json

from console import Console, FuncItem

from app.data.repositories import UserRepository
from app.domain.dtos import UserDto
from app.domain.use_cases import UserUseCase

from app.utilities.logger import logger


class Backup:
    def __init__(self, name: str, path: str) -> None:
        self._name = name
        self._path = path

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    @property
    def full_path(self) -> str:
        return os.path.join(self._path, self._name)


class RestoreBackup:
    def __init__(self, backup: Backup) -> None:
        self._backup = backup

    @property
    def backup(self) -> Backup:
        return self._backup

    def restore(self) -> None:
        raise NotImplementedError


class CreateBackup:
    def __init__(self, backup: Backup) -> None:
        self._backup = backup

    @property
    def backup(self) -> Backup:
        return self._backup

    def create(self) -> None:
        raise NotImplementedError


class SSHPlusBackup(Backup):
    def __init__(self):
        super().__init__('backup.vps', '/root/')


class GLBackup(Backup):
    def __init__(self):
        super().__init__('glbackup.tar.gz', '/root/')


class SSHPlusRestoreBackup(RestoreBackup):
    def get_limit_user(self, username: str) -> int:
        path = '/root/usuarios.db'

        try:
            with open(path, 'r') as file:
                for line in file:
                    if line.startswith(username):
                        return int(line.split()[1])
        except:
            pass

        return 1

    def get_expiration_date(self, username: str) -> str:
        command = 'chage -l {} | grep "Account expires"'
        data = os.popen(command.format(username)).read()
        expiration_date = data.strip().split(':')[-1].strip()
        return expiration_date

    def get_v2ray_uuid(self, username: str) -> t.Optional[str]:
        path = '/etc/v2ray/config.json'

        try:
            with open(path, 'r') as file:
                data = json.load(file)
                for list_data in data['inbounds']:
                    if 'settings' in list_data and 'clients' in list_data['settings']:
                        for client in list_data['settings']['clients']:
                            if client['email'] == username:
                                return client['id']
        except:
            pass

        return None

    def restore_users(self) -> None:
        path = '/etc/SSHPlus/senha/'
        for username in os.listdir(path):
            password = open(os.path.join(path, username), 'r').read().strip()
            limit = self.get_limit_user(username)
            expiration_date = self.get_expiration_date(username)
            v2ray_uuid = self.get_v2ray_uuid(username)

            user_dto = UserDto()
            user_dto.username = username
            user_dto.password = password
            user_dto.connection_limit = limit

            if expiration_date and expiration_date != 'never':
                user_dto.expiration_date = expiration_date

            if v2ray_uuid:
                user_dto.v2ray_uuid = v2ray_uuid

            repository = UserRepository()
            use_case = UserUseCase(repository)
            use_case.create(user_dto)

    def restore(self) -> None:
        logger.info('Restaurando SSHPlus...')

        command = 'tar -xvf {} --directory / >/dev/null 2>&1'
        result = os.system(command.format(self.backup.full_path))

        if result != 0:
            logger.error('Falha ao restaurar SSHPlus')
            return

        self.restore_users()
        logger.info('Restaurado com sucesso!')


class GLBackupRestoreBackup(RestoreBackup):
    def restore(self) -> None:
        logger.error('Desculpe, mas eu não fui implementado ainda!')


def restore_backup(backup: RestoreBackup) -> None:
    if not isinstance(backup, RestoreBackup):
        logger.error('O backup precisa ser uma instância de RestoreBackup!')
        Console.pause()
        return

    if not os.path.isfile(backup.backup.full_path):
        logger.error('Não foi encontrado o arquivo \'%s\'!', backup.backup.full_path)
        Console.pause()
        return

    backup.restore()
    Console.pause()


def choice_restore_backup() -> None:
    console = Console('RESTAURAR BACKUP')
    console.append_item(
        FuncItem(
            'SSHPLUS',
            lambda: restore_backup(SSHPlusRestoreBackup(SSHPlusBackup())),
        )
    )
    console.append_item(
        FuncItem(
            'GLBACKUP',
            lambda: restore_backup(GLBackupRestoreBackup(GLBackup())),
        )
    )
    console.show()


def tools_console_main() -> None:
    console = Console('GERENCIADOR DE FERRAMENTAS')
    console.append_item(FuncItem('VERFICAR ATUALIZAÇÕES', input))
    console.append_item(FuncItem('CRIAR BACKUP', input))
    console.append_item(FuncItem('RESTAURAR BACKUP', choice_restore_backup))

    console.show()
