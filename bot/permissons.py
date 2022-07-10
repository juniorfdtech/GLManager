import typing as t

from telebot.types import Message
from .bot import bot
from .bot_config import get_admin_id


class Permission:
    def __init__(self, user_id: int = None):
        self.user_id = user_id

    def is_granted(self) -> bool:
        raise NotImplementedError()


class AdminPermission(Permission):
    def is_granted(self) -> bool:
        return self.user_id == get_admin_id()


def permission_required(permission: t.Union[Permission, t.List[Permission]]):
    def decorator(func):
        def wrapper(message: Message):
            if isinstance(permission, list):
                for p in permission:
                    p.user_id = message.from_user.id

                    if p.is_granted():
                        return func(message)
            else:
                permission.user_id = message.from_user.id
                if permission.is_granted():
                    return func(message)

            bot.reply_to(message, '❌ Você não tem permissão para executar este comando')

        return wrapper

    return decorator


__all__ = ['permission_required', 'AdminPermission']
