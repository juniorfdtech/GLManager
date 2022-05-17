import typing as t

from datetime import datetime, timedelta
from .shellscript import exec_command

def load_all_users() -> t.List[str]:
    path = '/etc/passwd'
    data = []

    with open(path) as f:
        for line in f:
            split = line.split(':')
            if split[0] != 'nobody' and int(split[2]) >= 1000:
                data.append(split[0])

    return data


def find_user_by_name(name: str) -> t.Optional[str]:
    users = load_all_users()
    return next((user for user in users if user == name), None)


def count_users(users: t.List[str] = None) -> int:
    return len(users or load_all_users())


def get_pids_ssh(user: str) -> t.List[int]:
    command = f'ps -u {user}'
    output = exec_command(command)
    return [
        int(line.split()[0])
        for line in output.split('\n')[1:]
        if line and line.split()[-1] == 'sshd'
    ]

def days_to_date(days: int) -> str:
    return (datetime.now() + timedelta(days=days)).strftime('%d/%m/%Y')