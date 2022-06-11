import datetime

from app.__main__ import create_all

from app.data.repositories import UserRepository
from app.domain.entities import User

create_all()


def test_user_repository_create_user():
    user_repository = UserRepository()
    user = User()
    user.username = 'test'
    user.password = 'test'
    user.connection_limit = 10
    user.expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)

    user_created = user_repository.create(user)

    assert user_created.id is not None
    assert user_created.username == 'test'
    assert user_created.password == 'test'
    assert user_created.connection_limit == 10
    assert user_created.expiration_date == user.expiration_date

    user_repository.delete(user_created.id)


def test_user_repository_get_user():
    user_repository = UserRepository()
    user = User()
    user.username = 'test'
    user.password = 'test'
    user.connection_limit = 10
    user.expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)

    user_created = user_repository.create(user)

    user_got = user_repository.get_by_id(user_created.id)

    assert user_got.id is not None
    assert user_got.username == 'test'
    assert user_got.password == 'test'
    assert user_got.connection_limit == 10
    assert user_got.expiration_date == user.expiration_date

    user_repository.delete(user_created.id)


def test_user_repository_get_user_by_username():
    user_repository = UserRepository()
    user = User()
    user.username = 'test'
    user.password = 'test'
    user.connection_limit = 10
    user.expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)

    user_created = user_repository.create(user)

    user_got = user_repository.get_by_username(user.username)

    assert user_got.id is not None
    assert user_got.username == 'test'
    assert user_got.password == 'test'
    assert user_got.connection_limit == 10
    assert user_got.expiration_date == user.expiration_date

    user_repository.delete(user_created.id)
