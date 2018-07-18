# -*- coding: UTF-8 -*-
'''
腾讯 AI 文本（机器）翻译
地址：https://ai.qq.com/product/nlptrans.shtml#text
'''
import hashlib
from urllib import parse
import time
import random
import requests
from common import add_spaces


# https://ai.qq.com/doc/nlptrans.shtml 文档说明
API_INFO = {
    'APP_URL': 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_texttrans',
    'APP_ID': '1106966947',
    'APP_KEY': 'dmaHOxKBOhOZEYKf'
}


def get_sign_string(parser):
    '''
    签名有效期5分钟
    1.将 <key, value> 请求参数对按 key 进行字典升序排序，得到有序的参数对列表 N
    2.将列表 N 中的参数对按 URL 键值对的格式拼接成字符串，得到字符串 T（如：key1=value1&key2=value2），
        URL 键值拼接过程 value 部分需要 URL 编码，URL 编码算法用大写字母，例如 %E8，而不是小写 %e8
    3.将应用密钥以 app_key 为键名，组成 URL 键值拼接到字符串 T 末尾，得到字符串 S（如：key1=value1&key2=value2&app_key = 密钥)
    4.对字符串 S 进行 MD5 运算，将得到的 MD5 值所有字符转换成大写，得到接口请求签名
    :param parser:
    :return:
    '''
    params = sorted(parser.items())
    uri_str = parse.urlencode(params)

    sign_str = f'{uri_str}&app_key={API_INFO["APP_KEY"]}'

    # print('sign =', sign_str.strip())
    hash_md5 = hashlib.md5(sign_str.encode('utf-8'))
    return hash_md5.hexdigest().upper()


def get_nonce_str():
    '''
    获得 API 所需的随机字符串（非空且长度上限 32 字节）
    :return:(str)
    '''
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    nonce_lst = []
    for _ in range(random.randint(12, 20)):
        nonce_lst.append(random.choice(alphabet))
    return ''.join(nonce_lst)


def get_request_params(org_text):
    '''
    获取请求参数
    :param text:(str) 需翻译的文本
    :return:(dict) 所有请求参数
    '''
    req_dict = {
        'app_id': int(API_INFO['APP_ID']),
        'text': org_text,
        'time_stamp': int(time.time()),
        'nonce_str': get_nonce_str(),
        'type': 0
    }
    req_dict['sign'] = get_sign_string(req_dict)
    return req_dict


def translation(org_text):
    '''
    翻译文本
    :param text:(str) 纯中文，或者英文，自动转
    :return:(str) 对应的译文
    '''
    params = get_request_params(org_text)
    req = requests.post(API_INFO['APP_URL'], data=params)
    if req.status_code != 200:
        return None
    req_json = req.json()
    # print(req_json)
    if req_json['ret'] == 0:
        trans_text = req_json['data']['trans_text']
        trans_text = add_spaces.add_space(trans_text)

        trans_text = trans_text.replace('“','『').replace('”','』')

        return trans_text
    return None

if __name__ == '__main__':
    # TEXT_HELLO =  '\'.let\', \'.apply\', \'.also\', \'.run\', and \'with\''
    # TEXT_HELLO = ' are known as scope functions in Kotlin. We examine them and discuss what…'
    # TEXT_HELLO = 'you and "me"'
    TEXT_HELLO = 'you and me'
    # TEXT_HELLO = parse.quote_plus(TEXT_HELLO)
    # print(parse.quote(TEXT_HELLO))


    print(translation(TEXT_HELLO))

    # you = 'Kotlin 神秘化：什么是“范围函数”，为什么它们是特殊的？'
    # you = you.replace('“', '『').replace('”','』')
    # print(you)