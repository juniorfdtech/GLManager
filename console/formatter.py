#!/usr/bin/env python3

import os
import time

from .colors import COLOR_NAME, BG_COLOR_NAME, set_color
from .utils import get_ip_address


def get_app_version():
    try:
        from app import version

        return version.__version__
    except ImportError:
        return 'Unknown'


def clear_screen():
    os.system('clear' if os.name == 'nt' else 'cls')


def linux_distribution():
    path = '/etc/os-release'

    if os.path.exists(path):
        data = open(path).read().strip()
        data_dict = dict(line.split('=') for line in data.splitlines())

        name = data_dict.get('ID', 'Unknown').replace('"', '').upper()
        version = data_dict.get('VERSION_ID', 'Unknown').replace('"', '')

        return '%s %s' % (name, version)

    return 'Unknown'


def create_line(size=50, type='━', color=COLOR_NAME.GREEN, show=True):
    line = set_color(type * size, color)

    if show:
        print(line)

    return set_color(type * size, color)


def create_menu_bg(text, _type='-', size=50, color_bg=BG_COLOR_NAME.RED, set_pars=True):
    text_size = len(text) + 2 if set_pars else len(text)
    bar_size = (size - text_size) // 2

    if set_pars:
        return '%s\n%s%s%s%s%s\n%s' % (
            create_line(color=COLOR_NAME.BLUE, show=False),
            set_color(_type * bar_size, color_bg),
            set_color('[', COLOR_NAME.WHITE, color_bg),
            set_color(text, COLOR_NAME.GREEN, color_bg),
            set_color(']', COLOR_NAME.WHITE, color_bg),
            set_color(
                _type * (bar_size + 1 if (bar_size * 2) + text_size < size else bar_size), color_bg
            ),
            create_line(color=COLOR_NAME.BLUE, show=False),
        )

    return '%s\n%s%s%s\n%s' % (
        create_line(color=COLOR_NAME.BLUE, show=False),
        set_color(_type * bar_size, color_bg),
        set_color(text, COLOR_NAME.GREEN, color_bg),
        set_color(
            _type * (bar_size + 1 if (bar_size * 2) + text_size < size else bar_size), color_bg
        ),
        create_line(color=COLOR_NAME.BLUE, show=False),
    )


try:
    info = dict(
        (i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo').readlines()
    )
except:
    info = {'MemTotal': 0, 'MemFree': 0, 'Buffers': 0, 'Cached': 0}

ram_total = info['MemTotal'] / (2**20)
ram_used = (
    ram_total
    - info['MemFree'] / (2**20)
    - info['Buffers'] / (2**20)
    - info['Cached'] / (2**20)
)

RAM_INFO = (round(ram_total, 1), round(ram_used, 1))
SYSTEM = linux_distribution()

BANNER = create_menu_bg('GLTUNNEL MANAGER v' + get_app_version()) + '\n'
BANNER += set_color('OS: ', COLOR_NAME.RED) + set_color(SYSTEM, COLOR_NAME.GREEN).ljust(31)
BANNER += set_color('BY: ', COLOR_NAME.RED) + set_color('@Dutra01', COLOR_NAME.GREEN).ljust(27)
BANNER += (
    set_color('HORA: ', COLOR_NAME.RED)
    + set_color(time.strftime('%H:%M:%S'), COLOR_NAME.GREEN)
    + '\n'
)
BANNER += set_color('IP: ', COLOR_NAME.RED) + set_color(get_ip_address(), COLOR_NAME.GREEN).ljust(
    31
)
BANNER += set_color('RAM: ', COLOR_NAME.RED) + set_color(
    str(RAM_INFO[0]) + 'G', COLOR_NAME.GREEN
).ljust(26)
BANNER += (
    set_color('Em uso: ', COLOR_NAME.RED)
    + set_color(str(RAM_INFO[1]) + 'G', COLOR_NAME.GREEN)
    + '\n'
)


class Formatter:
    def __init__(self, columns=2):
        self.__columns = columns
        self.__format_chave = [set_color('[', COLOR_NAME.CYAN), set_color(']', COLOR_NAME.CYAN)]
        self.__format_choice = '%(choice)s %(point)s %(text)s'
        self.__items = None

    def set_item(self, item):
        self.__items = item

    def format_columm(self, items):
        choices_string = ''
        for idx, item in enumerate(items):
            choices_string += (
                self.__format_choice
                % {
                    'choice': self.__format_chave[0]
                    + set_color(
                        '%02d' % (idx + 1 if not item.is_exit_item else 0), COLOR_NAME.GREEN
                    )
                    + self.__format_chave[1],
                    'point': set_color('•', COLOR_NAME.GREEN),
                    'text': set_color(item.text, COLOR_NAME.RED),
                }
                + '\n'
            )
        return choices_string

    def format_two_columm(self, items):
        size_items1, size_items2 = len(items[0]), len(items[1])
        max_len = max(len(itm.text) for item in items for itm in item) + 8
        choices_string = ''
        for i in range(size_items1 + size_items2):
            if i < size_items2:
                choices_string += self.__format_choice % {
                    'choice': self.__format_chave[0]
                    + set_color('%02d' % (i + 1), COLOR_NAME.GREEN)
                    + self.__format_chave[1],
                    'point': set_color('•', COLOR_NAME.GREEN),
                    'text': set_color(items[0][i].text, COLOR_NAME.RED).ljust(max_len),
                }
                choices_string += (
                    self.__format_choice
                    % {
                        'choice': ' ' * 2
                        + self.__format_chave[0]
                        + set_color(
                            '%02d' % (size_items1 + i + 1 if not items[1][i].is_exit_item else 0),
                            COLOR_NAME.GREEN,
                        )
                        + self.__format_chave[1],
                        'point': set_color('•', COLOR_NAME.GREEN),
                        'text': set_color(items[1][i].text, COLOR_NAME.RED),
                    }
                    + '\n'
                )
            elif i < size_items1:
                choices_string += (
                    self.__format_choice
                    % {
                        'choice': self.__format_chave[0]
                        + set_color('%02d' % (i + 1), COLOR_NAME.GREEN)
                        + self.__format_chave[1],
                        'point': set_color('•', COLOR_NAME.GREEN),
                        'text': set_color(items[0][i].text, COLOR_NAME.RED),
                    }
                    + '\n'
                )
        return choices_string

    def format_items_two_colums(self, items):
        if len(items) < 20:
            items = [items[:10], items[10:]]
        else:
            if len(items) // 2 + len(items) // 2 < len(items):
                items = [items[: len(items) // 2 + 1], items[len(items) // 2 + 1 :]]
            else:
                items = [items[: len(items) // 2], items[len(items) // 2 :]]
        return self.format_two_columm(items)

    def build_banner(self):
        return BANNER

    def build_menu(self, title):
        return create_menu_bg(title) + '\n'

    def formatter(self, items, title):
        format_string = self.build_banner()
        format_string += self.build_menu(title)

        if self.__items:
            format_string += self.__items
            format_string += create_line(color=COLOR_NAME.BLUE, show=False) + '\n'
        if len(items) < 10 or self.__columns == 1:
            format_string += self.format_columm(items)
        else:
            format_string += self.format_items_two_colums(items)

        format_string += create_line(color=COLOR_NAME.BLUE, show=False)
        return format_string
