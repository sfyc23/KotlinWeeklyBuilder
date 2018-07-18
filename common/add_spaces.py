import sys
import functools


def is_latin(c):
    return ord(c) < 256


# Some characters should not have space on either side.
def allow_space(c):
    return not c.isspace() and not (c in '，。；「」：《》『』、[]（）*_')


def add_space_at_boundry(prefix, next_char):
    if len(prefix) == 0:
        return next_char
    if is_latin(prefix[-1]) != is_latin(next_char) and \
            allow_space(next_char) and allow_space(prefix[-1]):
        return prefix + ' ' + next_char
    else:
        return prefix + next_char


def add_space(str_):
    outstr = functools.reduce(add_space_at_boundry, str_, '')
    return outstr


if __name__ == '__main__':
    TEXT_HELLO = '我是CHina人'
    print(add_space(TEXT_HELLO))
