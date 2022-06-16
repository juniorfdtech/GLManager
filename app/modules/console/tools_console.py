import typing as t
import os
import json
import re

from console import Console, FuncItem, COLOR_NAME

from app.data.repositories import UserRepository
from app.domain.dtos import UserDto
from app.domain.use_cases import UserUseCase

from app.utilities.logger import logger
from app.version import __version__


class GLUpdate:
    def __init__(self):
        self.repository_url = 'https://github.com/DuTra01/GLManager.git'
        self.version_url = (
            'https://raw.githubusercontent.com/DuTra01/GLManager/master/app/version.py'
        )

    def check_update(self) -> bool:
        data = os.popen('curl -sL ' + self.version_url).read().strip()
        pattern = re.compile(r'__version__ = \'(.*)\'')
        match = pattern.search(data)

        if not match:
            return False

        version = match.group(1)
        if version == __version__:
            logger.warn('Nao foi encontrado atualizacoes')
            return False

        logger.success('Foi encontrada uma atualizacao')
        logger.success('Versao atual: ' + __version__)
        logger.success('Versao nova: ' + version)

        return True

    def update(self) -> None:
        os.chdir(os.path.expanduser('~'))

        if os.path.exists('GLManager'):
            os.system('rm -rf GLManager')

        os.system('echo \'y\' | pip3 uninstall GLManager') 

        os.system('git clone ' + self.repository_url)
        os.chdir('GLManager')
        os.system('pip3 install -r requirements.txt')
        os.system('python3 setup.py install')

        logger.success('Atualizacao realizada com sucesso')
        logger.success('Execute: `vps` para entrar no menu')
        exit(0)


def check_update() -> None:
    gl_update = GLUpdate()
    if gl_update.check_update():

        result = input(COLOR_NAME.YELLOW + 'Deseja atualizar? (S/N) ' + COLOR_NAME.RESET)

        if result.upper() == 'S':
            gl_update.update()

    Console.pause()


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
    def check_exists_user(self, username: str) -> bool:
        command = 'id {} >/dev/null 2>&1'
        result = os.system(command.format(username))
        return result == 0

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
            if not self.check_exists_user(username):
                return

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

            try:
                repository = UserRepository()
                use_case = UserUseCase(repository)
                use_case.create(user_dto)
            except Exception as e:
                logger.error(e)

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
    console.append_item(FuncItem('VERFICAR ATUALIZAÇÕES', check_update))
    console.append_item(FuncItem('CRIAR BACKUP', input))
    console.append_item(FuncItem('RESTAURAR BACKUP', choice_restore_backup))

    console.show()
