# -*- coding: utf-8 -*-
'''
解析猫眼电影 top 100
'''
import re
import json
from multiprocessing import Pool
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import bs4

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}

aw_base_url = 'https://androidweekly.net/'


def getAwArchive():
    try:
        res = requests.get('https://androidweekly.net/archive', headers=HEADERS)
        if res.status_code != 200:
            return None
    except RequestException:
        return None

    html_text = res.text
    # (.* ?)
    pattern = re.compile(r'<li.*?class="clearfix">.*?<span>(.*?)</span>.*?href="(.*?)">(.*?)</a>.*?</li>', re.S)
    items = re.findall(pattern, html_text)
    if items:
        print(items[0][0].strip())
        print(items[0][1].strip())
        print(items[0][2].strip())
        return f'{aw_base_url}{items[0][1]}'


def get_aw_data(url):
    list_article = []

    html_text = requests.get(url, headers=HEADERS).text
    soup_texts = BeautifulSoup(html_text, 'lxml')
    tables = soup_texts.find_all('table')

    for table in tables:
        if table.find('h2') or table.find('h5'):
            pass
        else:
            dict_article = {}

            td = table.find_all('td')[-2]

            title = td.find('a', class_='article-headline').string.strip()
            href = td.find('a', class_='article-headline').get('href').strip()
            brief = td.find('p').string.strip()
            domin = td.find('span').string.strip()[1:-1]

            dict_article['title'] = title
            dict_article['href'] = href
            dict_article['brief'] = brief
            dict_article['domin'] = domin
            list_article.append(dict_article)

        for item in list_article:
            print(item)


def get_kw_archive(url):
    url = 'https://us12.campaign-archive.com/home/?u=f39692e245b94f7fb693b6d82&id=93b2272cb6'

    html_text = requests.get(url, headers=HEADERS).text

    pattern = re.compile(r'<li.*?class="campaign">(.*?)<a href="(.*?)".*?>(.*?)</a>.*?</li>', re.S)
    items = re.findall(pattern, html_text)
    if items:
        time = items[0][0].strip()
        time = time[:time.index('-') - 1]
        link = items[0][1].strip()
        title = items[0][2].strip()

        print(link)
        return link


def get_kw_data(url):
    list_article = []

    html_text = requests.get(url, headers=HEADERS).text
    soup_texts = BeautifulSoup(html_text, 'lxml')
    tds = soup_texts.find_all('td', class_='mcnTextContent')[3]

    pre_bool = False

    # tds.find_all('p')
    # dict_article['title'] = title
    # dict_article['href'] = href
    # dict_article['brief'] = brief
    # dict_article['domin'] = domin

    if tds.find_all('p'):
        tds = tds.find_all('p')[0]

    # print(len(tds))
    dict_article = {}
    for td in tds.children:
        # if isinstance(td,str):
        # print(f'type = {type(td)}')
        # print(str(td))

        # if isinstance(td,bs4.element.NavigableString):

        std = str(td).strip()
        if not std or std == '<br/>' or std == '\xa0':
            continue
        # print(type(td))
        # print(std)

        if isinstance(td, bs4.element.NavigableString):
            if not pre_bool:
                continue

            if std.startswith('(') and std.endswith(')'):
                domain = std[1:-1]
                dict_article['domain'] = domain
            else:
                if dict_article.get('domain', ''):
                    brief = std.replace('\xa0', ' ')
                    dict_article['brief'] = brief
                    list_article.append(dict_article)

                dict_article = {}
                pre_bool = False
        else:

            if td.name != 'a':
                continue
            title = td.string.strip().replace('\xa0', ' ')
            if 'contact us' in title or 'us an email' in title:
                continue
            if not pre_bool:
                link = td.get('href')
                dict_article['title'] = title
                dict_article['link'] = link
            else:
                dict_article['title'] = dict_article.get('title', '') + title

            pre_bool = True

    for item in list_article:
        print(item)

        # list_article.append(dict_article)

        # for item in list_article:
        #     print(item)


def get_one_page(url):
    '''
    get current all movie info
    :param url: html url
    :return: html text
    '''
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    '''
    get one page data
    :param html: movie info
    :return: yield movie info
    '''
    pattern = re.compile(r'<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         + '.*?>(.*?)</a>.*?star">(.*?)</p>'
                         + '.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>'
                         + '.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    # ('31', 'http://p0.meituan.net/movie/...jpg,
    # '蝙蝠侠：黑暗骑士',
    # '主演：克里斯蒂安·贝尔,希斯·莱杰,艾伦·艾克哈特', '上映时间：2008-07-18(美国)', '9.', '3')
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }


'''
注意事项：1. 为什么 ensure_ascii=False？原因是 json 默认是以 ASCII 来解析 code 的，由于中文不在 ASCII 编码当中，因此就不让默认 ASCII 生效；
2. 要写入特定编码的文本文件，请给open()函数传入encoding参数，将字符串自动转换成指定编码。细心的童鞋会发现，
以'w'模式写入文件时，如果文件已存在，会直接覆盖（相当于删掉后新写入一个文件）。如果我们希望追加到文件末尾怎么办？可以传入'a'以追加（append）模式写入。
'''


def write_to_file(content):
    '''
    content write to result.text
    :param content: movie info content
    :return: None
    '''
    with open('result.txt', 'a', encoding='utf-8') as file:
        file.write(json.dumps(content, ensure_ascii=False) + '\n')
        file.close()

'''
对网页进行解析
'''


def main(offset):
    '''
    by offset get movie info
    :param offset: current page index
    :return: null
    '''
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    # POOL = Pool()
    # POOL.map(main, [i * 10 for i in range(10)])
    # print(getAwArchive())
    url = 'https://androidweekly.net/issues/issue-317'

    # get_aw_data(url)
    # get_kw_archive('')

    # url = 'http://eepurl.com/dArA89'
    url = 'https://us12.campaign-archive.com/?u=f39692e245b94f7fb693b6d82&id=ec3fe0b84f'
    get_kw_data(url)

    print('end')
