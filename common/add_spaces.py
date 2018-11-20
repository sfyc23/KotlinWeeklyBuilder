import sys
import functools


# Some characters should not have space on either side.
def allow_space(c):
    '''
    :param c: str
    :return: Bool True 允许加空格，False 不允许加空格
    '''
    return not c.isspace() and not (c in '，。；「」：《》『』、[]（）*_')


def is_latin(c):
    '''
    判断是否为英文字符，或者是数字
    :param c: str
    :return: Bool True 允许加空格，False 不允许加空格
    '''
    return ord(c) < 256


def add_space_at_boundry(prefix, next_char):
    '''
    通过前后字符判断，是否加上空格
    :param prefix: str 前面的字符
    :param next_char: str 后面的一个字符
    :return:str  返回当前位置已加空格（或不加）的 str
    '''
    if not prefix:
        return next_char
    if is_latin(prefix[-1]) != is_latin(next_char) and allow_space(next_char) and allow_space(prefix[-1]):
        return prefix + ' ' + next_char
    else:
        return prefix + next_char


def add_space(str_):
    '''
    为中英文之间加中空格。
    :param c: srt 文字
    :return: str 已处理的文字
    '''
    outstr = functools.reduce(add_space_at_boundry, str_, '')
    return outstr


if __name__ == '__main__':
    TEXT_HELLO = "I'm Chin中e牛se"
    print(add_space(TEXT_HELLO))
