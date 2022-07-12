from telebot import types

from .. import bot
from ..middleware import AdminPermission, DealerPermission, permission_required


def callback_query_menu():
    buttons = [
        [types.InlineKeyboardButton('CRIAR USUARIO', callback_data='create_user')],
        [types.InlineKeyboardButton('DELETAR USUARIO', callback_data='delete_user')],
        [types.InlineKeyboardButton('OBTER USUARIO', callback_data='get_user')],
        [types.InlineKeyboardButton('OBTER TODOS OS USUARIOS', callback_data='list_users')],
        [types.InlineKeyboardButton('MONITOR', callback_data='monitor')],
        [types.InlineKeyboardButton('REVENDA', callback_data='revenue')],
    ]

    return types.InlineKeyboardMarkup(buttons)


def callback_query_back_menu(message: str = '🔙MENU') -> types.InlineKeyboardMarkup:
    buttons = [
        [types.InlineKeyboardButton(message, callback_data='back_menu')],
    ]

    return types.InlineKeyboardMarkup(buttons)


def callback_query_back(callback_data, message: str = '🔙VOLTAR') -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(message, callback_data=callback_data)


def send_message_help(message: types.Message):
    bot.reply_to(
        message=message,
        text='<b>🖥COMANDOS DISPONIVEIS🖥</b>',
        reply_markup=callback_query_menu(),
    )


@bot.message_handler(commands=['help', 'start', 'menu'])
@permission_required([AdminPermission(), DealerPermission()])
def send_help(message: types.Message):
    send_message_help(message)


@bot.callback_query_handler(func=lambda call: call.data == 'back_menu')
@permission_required([AdminPermission(), DealerPermission()])
def back_menu(call: types.CallbackQuery):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='<b>🖥COMANDOS DISPONIVEIS🖥</b>',
        reply_markup=callback_query_menu(),
    )
