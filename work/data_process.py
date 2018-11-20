import json
import pandas as pd
from pandas import Series, DataFrame
from common import translation_utils


def clear_data(data_file_name):
    print('\n第 2 部分：开始数据处理：')
    with open(data_file_name, 'r', encoding='utf-8') as file:
        dict_data = json.loads(file.read())

    list_article = dict_data['data']

    def linkClear(dect_):
        link = dect_['link']
        if link.endswith('/'):
            dect_['link'] = link[0:len(link) - 1]
        return dect_

    list_article = list(map(linkClear, list_article))
    # print(list_article)

    new_lst = {name: [prop[name] for prop in list_article] for name in list_article[0].keys()}
    # print(new_lst)

    # 去重操作
    link_list = new_lst['link']
    del_index = []
    temp_list = []
    for i, item in enumerate(link_list):
        if link_list.count(item) >= 2:
            if not item in temp_list:
                temp_list.append(item)
            else:
                del_index.append(i)
        else:
            temp_list.append(item)

    # 删除多
    for de_i in del_index[::-1]:
        list_article.pop(de_i)

    print('6.开始翻译...')
    for dect_ in list_article:
        dect_['trans_title'] = translation_utils.translation(dect_['title'])
        dect_['trans_brief'] = translation_utils.translation(dect_['brief'])
    print('翻译完成...')

    def sort_list(x):
        link = x['domain']
        if 'github.com' in link:
            return 'zzzzzz'
        return link

    print('数据整理排序...')
    list_article = sorted(list_article, key=sort_list)

    dict_data['data'] = list_article

    with open(data_file_name, 'w+', encoding='utf-8') as file:
        file.write(json.dumps(dict_data, ensure_ascii=False) + '\n')

    print('数据处理完成...')
# type(list_article[0])
# yy = {}
# for i in yy.fromkeys()

# new_lst = {}


# print(type(list_article[0]))

# [n['priority'] for n in list_article]

# s1 = Series(list_article)
# print(s1)

# df = DataFrame(new_lst)
# print(df)


# list_article = sorted(list_article, key = lambda x: x['link'])
# for la in list_article:
#     print(f"{la['priority']}, {la['domain']}, {la['link']}")
#     # print(type(la))
