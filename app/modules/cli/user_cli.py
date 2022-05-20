import argparse
import typing as t

from datetime import datetime, timedelta

from app.utilities.validators import UserValidator
from app.utilities.utils import date_to_datetime, days_to_date
from app.domain.dtos import UserDto
from app.domain.use_cases import UserUseCase
from app.data.repositories import UserRepository

parser = argparse.ArgumentParser(description='User CLI')

parser.add_argument(
    '-u',
    '--username',
    help='Username',
    type=str,
)
parser.add_argument(
    '-p',
    '--password',
    help='Password',
    type=str,
)
parser.add_argument(
    '-l',
    '--limit-connections',
    type=int,
    default=1,
    help='Limit connections (default: %(default)s)',
)

parser.add_argument(
    '-e',
    '--expiration-date',
    type=str,
    default=(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
    help='Expiration date (default: %(default)s)',
)
parser.add_argument(
    '-d',
    '--days-to-expire',
    type=int,
    default=30,
    help='Days to expire (default: %(default)s)',
)

parser.add_argument(
    '-c',
    '--create',
    help='Create user',
    action='store_true',
)
parser.add_argument(
    '-U',
    '--update',
    help='Update user',
    action='store_true',
)
parser.add_argument(
    '-r',
    '--remove',
    help='Remove user',
    action='store_true',
)

parser.add_argument('-s', '--show', help='Show user', action='store_true')
parser.add_argument('-a', '--all', help='Show all users', action='store_true')


def create_user(
    username: str,
    password: str,
    limit_connections: int,
    expiration_date: datetime,
) -> None:
    user_dto = UserDto(
        username=username,
        password=password,
        connection_limit=limit_connections,
        expiration_date=expiration_date,
    )

    if not UserValidator.validate(user_dto):
        parser.print_help()
        return

    user_repository = UserRepository()
    user_use_case = UserUseCase(user_repository)
    user_use_case.create(user_dto)

    print('User created successfully')


def update_user(
    username: str,
    password: str = None,
    limit_connections: int = None,
    expiration_date: datetime = None,
) -> None:
    if password is None and limit_connections is None and expiration_date is None:
        print('Nothing to update')
        return

    user_repository = UserRepository()
    user_use_case = UserUseCase(user_repository)
    user = user_use_case.get_by_username(username)

    if user is None:
        print('User not found')
        return

    user_dto = UserDto.of(user)
    if password is not None:
        user_dto.password = password

    if limit_connections is not None:
        user_dto.connection_limit = limit_connections

    if expiration_date is not None:
        user_dto.expiration_date = expiration_date

    if not UserValidator.validate(user_dto):
        return

    user_use_case.update(user_dto)
    print('User updated successfully')


def delete_user(username: str) -> None:
    user_repository = UserRepository()
    user_use_case = UserUseCase(user_repository)
    user = user_use_case.get_by_username(username)

    if user is None:
        print('User not found')
        return

    user_use_case.delete(user)
    print('User deleted successfully')


def show_user(username: str) -> None:
    message = '-' * 20 + '\n'
    message += 'Username: %s\n'
    message += 'Password: %s\n'
    message += 'Limit connections: %s\n'
    message += 'Expiration date: %s\n'
    message += '-' * 20

    user_repository = UserRepository()
    user_use_case = UserUseCase(user_repository)
    user = user_use_case.get_by_username(username)

    if user is None:
        print('User not found')
        return

    print(
        message
        % (
            user.username,
            user.password,
            user.connection_limit,
            user.expiration_date,
        )
    )


def show_all_users() -> None:
    message = '-' * 20 + '\n'
    message += 'Username: %s\n'
    message += 'Password: %s\n'
    message += 'Limit connections: %s\n'
    message += 'Expiration date: %s\n'
    message += '-' * 20

    user_repository = UserRepository()
    user_use_case = UserUseCase(user_repository)
    users = user_use_case.get_all()

    if len(users) == 0:
        print('No users found')
        return

    for user in users:
        print(
            message
            % (
                user.username,
                user.password,
                user.connection_limit,
                user.expiration_date,
            )
        )


def main(args: t.List[str]) -> None:
    args = parser.parse_args(args)

    if args.create:
        create_user(
            username=args.username,
            password=args.password,
            limit_connections=args.limit_connections,
            expiration_date=date_to_datetime(
                days_to_date(args.days_to_expire) if args.days_to_expire else args.expiration_date
            ),
        )
    elif args.update:
        update_user(
            username=args.username,
            password=args.password,
            limit_connections=args.limit_connections,
            expiration_date=date_to_datetime(
                days_to_date(args.days_to_expire) if args.days_to_expire else args.expiration_date
            ),
        )
    elif args.remove:
        delete_user(args.username)

    if args.show:
        show_user(args.username)

    if args.all:
        show_all_users()
