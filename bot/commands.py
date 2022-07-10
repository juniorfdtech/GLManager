import datetime

from telebot.types import Message

from app.data.repositories import UserRepository
from app.domain.use_cases import UserUseCase
from app.domain.dtos import UserDto
from app.utilities.validators import UserValidator

from .bot import bot
from .permissons import AdminPermission, permission_required


def message_help() -> str:
    message = '''
    COMANDOS:

    /create_user - Cria um usuário
    ex: /create_user [Nome] [Senha] [Limite de conexões] [Dias de expiração]

    /delete_user - Deleta um usuário
    ex: /delete_user [Nome]

    /get_user - Obtém um usuário
    ex: /get_user [Nome]

    /get_all_users - Obtém todos os usuários
    ex: /get_all_users
    '''

    return message.strip().replace('    ', '')


def send_message_help(message: Message):
    bot.send_message(message.chat.id, message_help())


@bot.message_handler(commands=['help'])
def send_help(message: Message):
    send_message_help(message)


@bot.message_handler(regexp='/create_user (\w+) (\w+) (\d+) (\d+)')
@permission_required(AdminPermission())
def create_user(message: Message):
    username = message.text.split(' ')[1]
    password = message.text.split(' ')[2]

    limit_connections = message.text.split(' ')[3]
    expiration_date = message.text.split(' ')[4]

    if not limit_connections.isdigit():
        bot.reply_to(message, '❌ Limite de conexões deve ser um número')
        return

    if not expiration_date.isdigit():
        bot.reply_to(message, '❌ Data de expiração deve ser um número')
        return

    limit_connections = int(limit_connections)
    expiration_date = int(expiration_date)

    if limit_connections < 1:
        bot.reply_to(message, '❌ Limite de conexões deve ser maior que 0')
        return

    if expiration_date < 1:
        bot.reply_to(message, '❌ Data de expiração deve ser maior que 0')
        return

    user_use_case = UserUseCase(UserRepository())
    user_dto = UserDto.of(
        {
            'username': username,
            'password': password,
            'connection_limit': limit_connections,
            'expiration_date': datetime.datetime.now() + datetime.timedelta(days=expiration_date),
        }
    )

    if not UserValidator.validate(user_dto):
        bot.reply_to(message, '❌ <b>Nao foi possivel criar o usuario</b>')
        return

    try:
        user_created = user_use_case.create(user_dto)
    except Exception as e:
        bot.reply_to(message, 'Error: {}'.format(e))
        return

    message_reply = '<b>✅USUARIO CRIADO COM SUCESSO✅</b>\n\n'
    message_reply += '<b>👤Nome:</b> <code>{}</code>\n'.format(user_created.username)
    message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user_created.password)
    message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
        user_created.connection_limit
    )
    message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(
        user_created.expiration_date
    )

    bot.reply_to(message, message_reply, parse_mode='HTML')


@bot.message_handler(regexp='/delete_user (\w+)')
@permission_required(AdminPermission())
def delete_user(message: Message):
    username = message.text.split(' ')[1]

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        bot.reply_to(message, '❌ <b>Nao foi possivel encontrar o usuario</b>')
        return

    try:
        user_deleted = user_use_case.delete(user_dto.id)
    except Exception as e:
        bot.reply_to(message, 'Error: {}'.format(e))
        return

    bot.reply_to(message, '<b>✅USUARIO DELETADO COM SUCESSO✅</b>')


@bot.message_handler(regexp='/list_users')
@permission_required(AdminPermission())
def list_users(message: Message):
    user_use_case = UserUseCase(UserRepository())
    users = user_use_case.get_all()

    message_reply = '<b>📝Lista de usuarios📝</b>\n\n'
    for user in users:
        message_reply += '<b>👤Nome:</b> <code>{}</code>\n'.format(user.username)
        message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user.password)
        message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
            user.connection_limit
        )
        message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(user.expiration_date)
        message_reply += '\n'

    try:
        bot.reply_to(message, message_reply, parse_mode='HTML')
    except Exception as e:
        import os

        filename = os.urandom(16).hex() + '.txt'
        with open(filename, 'w') as f:
            f.write(message_reply)
            f.flush()

        bot.send_document(message.chat.id, open(filename, 'rb'))
        os.remove(filename)


@bot.message_handler(regexp='/get_user (\w+)')
@permission_required(AdminPermission())
def get_user(message: Message):
    username = message.text.split(' ')[1]

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        bot.reply_to(message, '❌ <b>Nao foi possivel encontrar o usuario</b>')
        return

    message_reply = '<b>👤Nome:</b> <code>{}</code>\n'.format(user_dto.username)
    message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user_dto.password)
    message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
        user_dto.connection_limit
    )
    message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(user_dto.expiration_date)

    bot.reply_to(message, message_reply, parse_mode='HTML')
