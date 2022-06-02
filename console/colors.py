#!/usr/bin/env python3

CSI = '\033[1;'
RESET = '\033[0m'


def code_to_chars(code):
    if code == 0:
        return RESET
    return CSI + str(code) + 'm'


class CodesName(object):
    def __init__(self):
        for name in dir(self):
            if not name.startswith('_'):
                value = getattr(self, name)
                setattr(self, name, code_to_chars(value))


class CodesID(object):
    def __init__(self):
        for name in dir(self):
            if not name.startswith('_'):
                value = getattr(self, name)
                setattr(self, name, value)


class COLOR_ID(CodesID):
    BLACK = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 34
    MAGENTA = 95
    CYAN = 96
    WHITE = 97
    RESET = 0
    END = 0


class BACK_COLOR_ID(CodesID):
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 0
    END = 0


class COLOR_NAME(CodesName, COLOR_ID):
    pass


class BACK_COLOR_NAME(CodesName, BACK_COLOR_ID):
    pass


def set_color_id(text, color_id):
    return RESET + code_to_chars(color_id) + str(text) + RESET


def set_color(text, *colors):

    return RESET + ''.join(colors) + str(text) + RESET


COLOR_ID = COLOR_ID()
COLOR_NAME = COLOR_NAME()
BG_COLOR_NAME = BACK_COLOR_NAME()
BG_COLOR_ID = BACK_COLOR_ID()

__all__ = ['COLOR_ID', 'COLOR_NAME', 'BG_COLOR_ID', 'BG_COLOR_ID', 'set_color']
