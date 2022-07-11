import datetime

from telebot.types import Message, CallbackQuery
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

from app.data.repositories import UserRepository
from app.domain.use_cases import UserUseCase
from app.domain.dtos import UserDto
from app.utilities.validators import UserValidator
from app.utilities.utils import count_connections

from .bot import bot
from .permissons import AdminPermission, permission_required


def send_message_user_created(message: Message, user_created: UserDto):
    message_reply = '<b>✅USUARIO CRIADO COM SUCESSO✅</b>\n\n'
    message_reply += '<b>👤Nome:</b> <code>{}</code>\n'.format(user_created.username)
    message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user_created.password)
    message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
        user_created.connection_limit
    )
    message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(
        user_created.expiration_date.strftime('%d/%m/%Y')
    )

    bot.reply_to(
        message=message,
        text=message_reply,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


def callback_query_menu():
    buttons = [
        [InlineKeyboardButton('CRIAR USUARIO', callback_data='create_user')],
        [InlineKeyboardButton('DELETAR USUARIO', callback_data='delete_user')],
        [InlineKeyboardButton('OBTER USUARIO', callback_data='get_user')],
        [InlineKeyboardButton('OBTER TODOS OS USUARIOS', callback_data='list_users')],
        [InlineKeyboardButton('MONITOR', callback_data='monitor')],
    ]

    return InlineKeyboardMarkup(buttons)


def callback_query_back_menu(message: str = '🔙MENU') -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(message, callback_data='back_menu')],
    ]

    return InlineKeyboardMarkup(buttons)


def callback_query_back(callback_data, message: str = '🔙VOLTAR') -> InlineKeyboardButton:
    return InlineKeyboardButton(message, callback_data=callback_data)


def send_message_help(message: Message):
    bot.reply_to(
        message=message,
        text='<b>🖥COMANDOS DISPONIVEIS🖥</b>',
        reply_markup=callback_query_menu(),
    )


@bot.message_handler(commands=['help', 'start', 'menu'])
@permission_required(AdminPermission())
def send_help(message: Message):
    send_message_help(message)


@bot.callback_query_handler(func=lambda call: call.data == 'back_menu')
@permission_required(AdminPermission())
def back_menu(call: CallbackQuery):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='COMANDOS DISPONIVEIS:',
        reply_markup=callback_query_menu(),
    )


@bot.callback_query_handler(func=lambda query: query.data == 'create_user')
@permission_required(AdminPermission())
def callback_query_create_user(query: CallbackQuery):
    message = bot.send_message(
        chat_id=query.message.chat.id,
        text='<b>👤Nome do usuario:</b>',
        parse_mode='HTML',
        reply_markup=ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, proccess_username)


def proccess_username(message: Message):
    username = message.text

    if not UserValidator.validate_username(username):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ NOME DE USUARIO INVALIDO',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    reply_text = '<b>👤Nome do usuario: </b> <code>{}</code>\n'.format(username)
    reply_text += '<b>🔐Senha:</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        parse_mode='HTML',
        reply_markup=ForceReply(selective=True),
    )
    bot.register_next_step_handler(message, proccess_password, username=username)


def proccess_password(message: Message, username: str):
    password = message.text

    if not UserValidator.validate_password(password):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ SENHA INVALIDA',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    reply_text = '<b>👤Nome do usuario: </b> <code>{}</code>\n'.format(username)
    reply_text += '<b>🔐Senha:</b> <code>{}</code>\n'.format(password)
    reply_text += '<b>🚫Limite de conexões:</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        parse_mode='HTML',
        reply_markup=ForceReply(selective=True),
    )

    bot.register_next_step_handler(
        message,
        proccess_limit_connections,
        username=username,
        password=password,
    )


def proccess_limit_connections(message: Message, username: str, password: str):
    limit = message.text

    if not UserValidator.validate_connection_limit(limit):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ LIMITE DE CONEXOES INVALIDO',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    reply_text = '<b>👤Nome do usuario: </b> <code>{}</code>\n'.format(username)
    reply_text += '<b>🔐Senha:</b> <code>{}</code>\n'.format(password)
    reply_text += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(limit)
    reply_text += '<b>📆Data de expiração:</b>'

    message = bot.send_message(
        chat_id=message.chat.id,
        text=reply_text,
        parse_mode='HTML',
        reply_markup=ForceReply(selective=True),
    )

    bot.register_next_step_handler(
        message,
        proccess_expiration_date,
        username=username,
        password=password,
        limit=limit,
    )


def proccess_expiration_date(message: Message, username: str, password: str, limit: str):
    expiration = message.text

    if not UserValidator.validate_expiration_date(expiration):
        bot.send_message(
            chat_id=message.chat.id,
            text='❌ DATA DE EXPIRACAO INVALIDA',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    user_use_case = UserUseCase(UserRepository())
    user_created = user_use_case.create(
        UserDto.of(
            {
                'username': username,
                'password': password,
                'connection_limit': limit,
                'expiration_date': datetime.datetime.now()
                + datetime.timedelta(days=int(expiration)),
            }
        )
    )

    send_message_user_created(message, user_created)


@bot.message_handler(regexp='/create_user (\w+) (\w+) (\d+) (\d+)')
@permission_required(AdminPermission())
def create_user(message: Message):
    username = message.text.split(' ')[1]
    password = message.text.split(' ')[2]

    limit_connections = message.text.split(' ')[3]
    expiration_date = message.text.split(' ')[4]

    if not limit_connections.isdigit():
        bot.reply_to(
            message,
            '❌ Limite de conexões deve ser um número',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    if not expiration_date.isdigit():
        bot.reply_to(
            message,
            '❌ Data de expiração deve ser um número',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    limit_connections = int(limit_connections)
    expiration_date = int(expiration_date)

    if limit_connections < 1:
        bot.reply_to(
            message,
            '❌ Limite de conexões deve ser maior que 0',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    if expiration_date < 1:
        bot.reply_to(
            message,
            '❌ Data de expiração deve ser maior que 0',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
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
        bot.reply_to(
            message,
            '❌ <b>Nao foi possivel criar o usuario</b>',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    try:
        user_created = user_use_case.create(user_dto)
    except Exception as e:
        bot.reply_to(message, 'Error: {}'.format(e))
        return

    send_message_user_created(message, user_created)


@bot.callback_query_handler(func=lambda query: query.data == 'delete_user')
@permission_required(AdminPermission())
def callback_query_delete_user(query: CallbackQuery):
    message = bot.send_message(
        chat_id=query.message.chat.id,
        text='<b>👤Nome do usuario: </b>',
        parse_mode='HTML',
        reply_markup=ForceReply(selective=True),
    )

    bot.register_next_step_handler(message, proccess_username_delete)


def proccess_username_delete(message: Message):
    username = message.text

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        bot.send_message(
            chat_id=message.chat.id,
            text='<b>❌ USUARIO NAO ENCONTRADO</b>',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    user_use_case.delete(user_dto.id)

    reply_text = '<b>✅USUARIO DELETADO COM SUCESSO✅</b>\n'
    reply_text += '<b>👤Nome do usuario: </b> <code>{}</code>'.format(username)

    bot.reply_to(
        message,
        reply_text,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


@bot.message_handler(regexp='/delete_user (\w+)')
@permission_required(AdminPermission())
def delete_user(message: Message):
    username = message.text.split(' ')[1]

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        bot.reply_to(
            message,
            '❌ <b>Nao foi possivel encontrar o usuario</b>',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    try:
        user_use_case.delete(user_dto.id)
    except Exception as e:
        bot.reply_to(message, 'Error: {}'.format(e))
        return

    reply_text = '<b>✅USUARIO DELETADO COM SUCESSO✅</b>\n'
    reply_text += '<b>👤Nome do usuario: </b> <code>{}</code>'.format(username)

    bot.reply_to(
        message,
        reply_text,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


@bot.callback_query_handler(func=lambda query: query.data == 'list_users')
@permission_required(AdminPermission())
def callback_query_list_users(query: CallbackQuery):
    user_use_case = UserUseCase(UserRepository())
    users = user_use_case.get_all()

    if not users:
        bot.reply_to(query.message, '❌ <b>Nao foi possivel encontrar usuarios</b>')
        return

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
        bot.edit_message_text(
            message_reply,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )

    except Exception as e:
        import os

        filename = os.urandom(16).hex() + '.txt'
        with open(filename, 'w') as f:
            f.write(message_reply)
            f.flush()

        bot.send_document(
            query.message.chat.id,
            open(filename, 'rb'),
            reply_markup=callback_query_back_menu(),
        )
        os.remove(filename)


@bot.message_handler(regexp='/list_users')
@permission_required(AdminPermission())
def list_users(message: Message):
    user_use_case = UserUseCase(UserRepository())
    users = user_use_case.get_all()

    if not users:
        bot.reply_to(users, '❌ <b>Nao foi possivel encontrar usuarios</b>')
        return

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
        bot.reply_to(
            message,
            message_reply,
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
    except Exception as e:
        import os

        filename = os.urandom(16).hex() + '.txt'
        with open(filename, 'w') as f:
            f.write(message_reply)
            f.flush()

        bot.send_document(
            message.chat.id,
            open(filename, 'rb'),
            reply_markup=callback_query_back_menu(),
        )
        os.remove(filename)


@bot.callback_query_handler(func=lambda query: query.data == 'get_user')
@permission_required(AdminPermission())
def callback_query_get_user(query: CallbackQuery):
    user_use_case = UserUseCase(UserRepository())
    users = user_use_case.get_all()

    if not users:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text='❌ <b>Nao foi possivel encontrar usuarios</b>',
            parse_mode='HTML',
            reply_markup=callback_query_back_menu(),
        )
        return

    buttons = []

    for i in range(0, len(users), 2):
        if i + 1 >= len(users):
            buttons.append(
                [
                    InlineKeyboardButton(
                        users[i].username, callback_data='get_user_' + users[i].username
                    )
                ]
            )
            continue

        buttons.append(
            [
                InlineKeyboardButton(
                    text=users[i].username,
                    callback_data='get_user_' + users[i].username,
                ),
                InlineKeyboardButton(
                    text=users[i + 1].username,
                    callback_data='get_user_' + users[i + 1].username,
                ),
            ]
        )

    buttons.extend(callback_query_back_menu().keyboard)

    reply_markup = InlineKeyboardMarkup(buttons)

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text='<b>📝Selecione um usuario📝</b>',
        reply_markup=reply_markup,
        parse_mode='HTML',
    )


@bot.callback_query_handler(func=lambda query: query.data.startswith('get_user_'))
@permission_required(AdminPermission())
def callback_query_get_user(query: CallbackQuery):
    username = query.data.split('_')[-1]

    user_use_case = UserUseCase(UserRepository())
    user_dto = user_use_case.get_by_username(username)

    if not user_dto:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text='❌ <b>Nao foi possivel encontrar usuario</b>',
            reply_markup=callback_query_back_menu(),
            parse_mode='HTML',
        )
        return

    message_reply = '<b>👤Nome:</b> <code>{}</code>\n'.format(user_dto.username)
    message_reply += '<b>🔐Senha:</b> <code>{}</code>\n'.format(user_dto.password)
    message_reply += '<b>🚫Limite de conexões:</b> <code>{}</code>\n'.format(
        user_dto.connection_limit
    )
    message_reply += '<b>📆Data de expiração:</b> <code>{}</code>\n'.format(user_dto.expiration_date)

    buttons = callback_query_back_menu().keyboard
    buttons[0].append(callback_query_back('get_user'))

    reply_markup = InlineKeyboardMarkup(buttons)

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=message_reply,
        reply_markup=reply_markup,
        parse_mode='HTML',
    )


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

    bot.reply_to(
        message,
        message_reply,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


@bot.message_handler(regexp='/monitor')
@permission_required(AdminPermission())
def monitor(message: Message):
    user_use_case = UserUseCase(UserRepository())
    users = user_use_case.get_all()

    if not users:
        bot.reply_to(message, '❌ <b>Nao foi possivel encontrar usuarios</b>')
        return

    message_reply = '<b>MOME | LIMITE | CONEXOES | DATA DE EXPIRACAO</b>\n\n'
    width_user = max(len(user.username) for user in users)
    width_limit = max(len(str(user.connection_limit)) for user in users)

    for user in user_use_case.get_all():
        message_reply += '<code>'
        message_reply += '{} | '.format(user.username.ljust(width_user))
        message_reply += '{} | '.format(('%02d' % user.connection_limit).ljust(width_limit))
        message_reply += '{} | '.format(('%02d' % count_connections(user.username)).ljust(2))
        message_reply += '{}'.format(user.expiration_date.strftime('%d/%m/%Y'))
        message_reply += '</code>\n'

    bot.reply_to(
        message,
        message_reply,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )


@bot.callback_query_handler(func=lambda query: query.data == 'monitor')
@permission_required(AdminPermission())
def callback_query__monitor(query: CallbackQuery):
    user_use_case = UserUseCase(UserRepository())
    users = user_use_case.get_all()

    if not users:
        bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text='❌ <b>Nao foi possivel encontrar usuarios</b>',
            reply_markup=callback_query_back_menu(),
            parse_mode='HTML',
        )
        return

    message_reply = '<b>MOME | LIMITE | CONEXOES | DATA DE EXPIRACAO</b>\n\n'
    width_user = max(len(user.username) for user in users)
    width_limit = max(len(str(user.connection_limit)) for user in users)

    for user in user_use_case.get_all():
        message_reply += '<code>'
        message_reply += '{} | '.format(user.username.ljust(width_user))
        message_reply += '{} | '.format(('%02d' % user.connection_limit).ljust(width_limit))
        message_reply += '{} | '.format(('%02d' % count_connections(user.username)).ljust(2))
        message_reply += '{}'.format(user.expiration_date.strftime('%d/%m/%Y'))
        message_reply += '</code>\n'

    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=message_reply,
        parse_mode='HTML',
        reply_markup=callback_query_back_menu(),
    )
