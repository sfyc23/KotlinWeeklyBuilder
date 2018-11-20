# -*- coding: utf-8 -*-
'''
解析网页
'''
import re
import json
from multiprocessing import Pool
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import bs4
from work import file_name

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}


def get_aw_archive():
    '''
    获取 androidWeekly 中的最新一期的 url。
    :return:(str) 最新一期 url
    '''
    AW_BASE_URL = 'https://androidweekly.net/'
    AW_ARCHIVE_URL = 'https://androidweekly.net/archive'
    try:
        res = requests.get(AW_ARCHIVE_URL, headers=HEADERS)
        if res.status_code != 200:
            return None
    except RequestException:
        return None

    html_text = res.text
    pattern = re.compile(r'<li.*?class="clearfix">.*?<span>(.*?)</span>.*?href="(.*?)">(.*?)</a>.*?</li>', re.S)
    items = re.findall(pattern, html_text)
    if items:
        # print(items[0][0].strip())  # 2018-07-15
        # print(items[0][1].strip())  # /issues/issue-318
        # print(items[0][2].strip())  # Issue #318

        link = f'{AW_BASE_URL}{items[0][1]}'
        index = link[link.find('-') + 1:]
        title = f'Android Weekly - {index}'
        return title, link
    return None


def get_aw_data(url):
    '''
    获取 androidWeely by kotlin 的数据
    :param url:(str) 地址 url
    :return:(list) 返回数据集合
    '''

    list_article = []

    try:
        html_text = requests.get(url, headers=HEADERS).text
    except RequestException as exception:
        print(f"请求 androidWeekly data 出错：{exception}")
        return None

    soup_texts = BeautifulSoup(html_text, 'lxml')
    tables = soup_texts.find_all('table')

    for table in tables:
        if table.find('h2') or table.find('h5'):
            continue

        td_item = table.find_all('td')[-2]
        title = td_item.find('a', class_='article-headline').string.strip()
        href = td_item.find('a', class_='article-headline').get('href').strip()
        brief = td_item.find('p').string.strip()
        domain = td_item.find('span').string.strip()[1:-1]

        # priority 表示数据的优先级。用于数据筛选
        dict_article = {'priority': 1}
        dict_article['title'] = title
        dict_article['link'] = href
        dict_article['brief'] = brief
        dict_article['domain'] = domain

        # 只保留标题与简要中有 kotlin 关键字的数据
        if 'kotlin' in title.lower() or 'kotlin' in brief.lower():
            list_article.append(dict_article)

        # for item in list_article:
        #     print(item)
    return list_article


def get_kw_archive():
    '''
    获取 kotlinWeekly 中的最新一期的 url。
    :return:(str) 最新一期的 标题、 url、期数
    '''
    KW_ARCHIVE_URL = 'https://us12.campaign-archive.com/home/?u=f39692e245b94f7fb693b6d82&id=93b2272cb6'

    try:
        html_text = requests.get(KW_ARCHIVE_URL, headers=HEADERS).text
    except RequestException as exception:
        print(f"请求 kotlinWeekly archive 出错：{exception}")
        return None, None, None

    pattern = re.compile(r'<li.*?class="campaign">(.*?)<a href="(.*?)".*?>(.*?)</a>.*?</li>', re.S)
    items = re.findall(pattern, html_text)
    if items:
        time = items[0][0].strip()  # 07/15/2018 -
        time = time[:time.find('-') - 1]
        link = items[0][1].strip()

        title = items[0][2].strip()  # Kotlin Weekly #102
        index = title[title.find('#') + 1:]
        title = f'Kotlin Weekly - {index}'

        return title, link, index
    return None


def get_kw_data(url):
    '''
    获取 kotlinWeekly 的数据
    :param url:(str) 地址 url
    :return:(list) 返回数据集合
    '''

    list_article = []
    try:
        html_text = requests.get(url, headers=HEADERS).text
    except RequestException as exception:
        print(f"请求 kotlinWeekly data 出错：{exception}")
        return None

    soup_texts = BeautifulSoup(html_text, 'lxml')
    tds = soup_texts.find_all('td', class_='mcnTextContent')[3]

    pre_bool = False
    for td_content in tds.find_all('p'):
        # 主目录下至少得20个支点以上吧。
        if len(list(td_content.children)) > 20:
            tds = td_content
            break

    dict_article = {'priority': 2}
    for td_item in tds.children:
        std = str(td_item).strip()
        if not std or std == '<br/>' or std == '\xa0':
            continue
        # print(type(td))
        # print(std)
        if isinstance(td_item, bs4.element.NavigableString):
            if not pre_bool:
                continue
            # 如：(medium.com)
            if std.startswith('(') and std.endswith(')'):
                dict_article['domain'] = std[1:-1]
            else:
                if dict_article.get('domain', ''):
                    brief = std.replace('\xa0', ' ')
                    dict_article['brief'] = brief
                    list_article.append(dict_article)
                dict_article = {'priority': 2}
                pre_bool = False
        else:
            if td_item.name != 'a':
                continue
            title = td_item.string.strip().replace('\xa0', ' ')
            if 'contact us' in title or 'us an email' in title or 'Pusher' in title:
                continue
            if not pre_bool:
                link = td_item.get('href')
                dict_article['title'] = title
                dict_article['link'] = link
            else:
                dict_article['title'] = dict_article.get('title', '') + title
            pre_bool = True
    # for item in list_article:
    #     print(item)
    return list_article


# https://medium.com/mindorks/kotlin-weekly-update-47-bd993cb8751
def get_kw_medium_act():
    '''
    获取 medium —— kotlinWeekly 中的最新一期的 url。
    :return:(str) 最新一期的标题与 url
    '''
    MEDIUM_URL = 'https://medium.com/@pranaypatel'

    try:
        html_text = requests.get(MEDIUM_URL, headers=HEADERS).text
    except RequestException as exception:
        print(f"请求 medium 出错：{exception}")
        return None, None

    # div#root >div>section>div.div

    soup_texts = BeautifulSoup(html_text, 'lxml')
    content_divs = soup_texts.find('div', id='root').div.section.contents[1].div.contents[3:]

    for node in content_divs:
        link = node.div.contents[1].get('href')

        title = node.find('h1').string.strip()
        if 'Kotlin Weekly' in title:
            link = f'https://medium.com{link}'
            return title, link
    return None, None


def get_kw_medium_data(url):
    '''
    获取 Meduim 中 kotlinWeekly 的数据
    :param url:(str) 地址 url
    :return:(list) 返回数据集合
    '''
    list_article = []
    try:
        html_text = requests.get(url, headers=HEADERS).text
    except RequestException as exception:
        print(f"请求 medium androidWeekly data 出错：{exception}")
        return None,

    pattern = re.compile(r'https?://(.*?)/.*?', re.S)

    soup_texts = BeautifulSoup(html_text, 'lxml')
    tdss = soup_texts.find_all('div', class_='section-inner sectionLayout--insetColumn')

    for tds in tdss:
        div_td = tds.find_all('div')
        if not div_td:
            continue
        if not div_td[0].find_all('strong'):
            continue
        if 'Advance Kotlin' in div_td[0].find('strong').string:
            continue

        for td_item in div_td:

            title = td_item.find('strong').string
            if "Kotlin Weekly Update" in title:
                continue

            brief = td_item.find('em').string
            link = td_item.find('a').get('href')

            # 从 link 中取出网址的 baseurl
            domain = re.findall(pattern, link)[0]

            dict_article = {'priority': 3}
            dict_article['title'] = title
            dict_article['link'] = link
            dict_article['brief'] = brief
            dict_article['domain'] = domain

            list_article.append(dict_article)

    # for item in list_article:
    #     print(item)

    # print(len(divds))
    return list_article


def download_data():
    '''
    1.获取 AndroidWeekly 中的内容
    2.获取 KotlinWeekly 中的内容
    3.获取 Medium KotionWeekly 中的内容
    :return:
    '''
    dict_data = {}
    list_article = []
    list_domain = []

    print("第 1 部分：开始爬取数据")

    print('1. 爬取 Android Weekly 中的数据..')
    aw_title, aw_link = get_aw_archive()
    if aw_link:
        aw_data = get_aw_data(aw_link)
        list_article.extend(aw_data)
        list_domain.append({'title': aw_title, 'link': aw_link})
        print(f'Android Weekly 中 取得 {len(aw_data)} 条数据')

    print('2. 爬取 Kotlin Weekly 中的数据..')
    kw_title, kw_archive, index = get_kw_archive()
    if kw_archive:
        kw_data = get_kw_data(kw_archive)
        list_article.extend(kw_data)
        list_domain.append({'title': kw_title, 'link': kw_archive})
        print(f'Kotlin Weekly 中 取得 {len(kw_data)} 条数据')

    print('3. 爬取 Medium Kotlin Weekly 中的数据..')
    # mkw_title, mkw_archive = get_kw_medium_act()
    # if mkw_archive:
    #     kw_medium_data = get_kw_medium_data(mkw_archive)
    #     list_article.extend(kw_medium_data)
    #     list_domain.append({'title': mkw_title, 'link': mkw_archive})
    #     print(f'Medium Kotlin Weekly 中 取得 {len(kw_medium_data)} 条数据')

    dict_data['data'] = list_article
    dict_data['domain'] = list_domain

    # print(dict_data)

    # for item in list_article:
    #     print(item)
    # #

    print('数据爬取完成\n4. 将数据保存本地 json 文件中')

    data_file_name = file_name.get_data_name(index)

    # 将数据保存本地txt文件中
    with open(data_file_name, 'w+', encoding='utf-8') as file:
        file.write(json.dumps(dict_data, ensure_ascii=False) + '\n')
    print('数据已保存成功。。')
    return index, data_file_name


if __name__ == '__main__':
    # download_data()
    # get_aw_data(url)
    # get_kw_archive('')

    # url = 'http://eepurl.com/dArA89'
    # url = 'https://us12.campaign-archive.com/?u=f39692e245b94f7fb693b6d82&id=ec3fe0b84f'
    # get_kw_data(url)

    # url = 'https://medium.com/mindorks/kotlin-weekly-update-47-bd993cb8751'
    my_url = 'https://medium.com/mindorks/kotlin-weekly-update-57-7884d7436161'
    for ll in get_kw_medium_data(my_url):
        print(ll)

    # get_kw_medium_act()
    # print((get_kw_data("https://us12.campaign-archive.com/?u=f39692e245b94f7fb693b6d82&id=3dfa30b84e")))

    print('end')
