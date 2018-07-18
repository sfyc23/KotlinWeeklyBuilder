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


def getAwArchive():
    print("第 1 部分：开始爬取数据")
    aw_base_url = 'https://androidweekly.net/'
    try:
        res = requests.get('https://androidweekly.net/archive', headers=HEADERS)
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

        link = f'{aw_base_url}{items[0][1]}'
        index = link[link.index('-') + 1:]
        title = f'Android Weekly - {index}'
        return title, link
    return None


def get_aw_data(url):
    list_article = []

    html_text = requests.get(url, headers=HEADERS).text
    soup_texts = BeautifulSoup(html_text, 'lxml')
    tables = soup_texts.find_all('table')

    for table in tables:
        if table.find('h2') or table.find('h5'):
            pass
        else:
            dict_article = {'priority': 1}

            td = table.find_all('td')[-2]
            title = td.find('a', class_='article-headline').string.strip()
            href = td.find('a', class_='article-headline').get('href').strip()
            brief = td.find('p').string.strip()
            domain = td.find('span').string.strip()[1:-1]

            dict_article['title'] = title
            dict_article['link'] = href
            dict_article['brief'] = brief
            dict_article['domain'] = domain

            if 'kotlin' in title.lower() or 'kotlin' in brief.lower():
                list_article.append(dict_article)

        # for item in list_article:
        #     print(item)
    return list_article


def get_kw_archive():
    url = 'https://us12.campaign-archive.com/home/?u=f39692e245b94f7fb693b6d82&id=93b2272cb6'

    html_text = requests.get(url, headers=HEADERS).text

    pattern = re.compile(r'<li.*?class="campaign">(.*?)<a href="(.*?)".*?>(.*?)</a>.*?</li>', re.S)
    items = re.findall(pattern, html_text)
    if items:
        time = items[0][0].strip()  # 07/15/2018 -
        time = time[:time.index('-') - 1]
        link = items[0][1].strip()

        title = items[0][2].strip()  # Kotlin Weekly #102
        index = title[title.index('#') + 1:]
        title = f'Kotlin Weekly - {index}'

        return title, link, index
    return None


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

    dict_article = {'priority': 2}
    for td in tds.children:
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
                dict_article = {'priority': 2}
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

    # for item in list_article:
    #     print(item)
    return list_article


# https://medium.com/mindorks/kotlin-weekly-update-47-bd993cb8751
def get_kw_medium_act():
    url = 'https://medium.com/@pranaypatel'
    html_text = requests.get(url, headers=HEADERS).text
    soup_texts = BeautifulSoup(html_text, 'lxml')
    content_divs = soup_texts.find('div', id='root').div.section.contents[1].div.contents[3:]

    for cc in content_divs:
        link = cc.div.contents[1].get('href')

        title = cc.find('h1').string.strip()
        if 'Kotlin Weekly' in title:
            link = f'https://medium.com{link}'
            return title, link
    return None


def get_kw_medium_data(url):
    list_article = []

    html_text = requests.get(url, headers=HEADERS).text
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

        for td in div_td:
            dict_article = {'priority': 3}

            brief = td.find('em').string
            link = td.find('a').get('href')
            title = td.find('strong').string

            pattern = re.compile(r'https?://(.*?)/.*?', re.S)
            domain = re.findall(pattern, link)[0]

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

    dict_data = {}
    list_article = []
    list_domain = []

    print('1. 爬取 Android Weekly 中的数据..')
    # aw_title, aw_link = getAwArchive()
    # if aw_link:
    #     list_article.extend(get_aw_data(aw_link))
    #     list_domain.append({'title': aw_title, 'link': aw_link})

    print('2. 爬取 Kotlin Weekly 中的数据..')
    kw_title, kw_archive, index = get_kw_archive()
    if kw_archive:
        list_article.extend(get_kw_data(kw_archive))
        list_domain.append({'title': kw_title, 'link': kw_archive})

    print('3. 爬取 medium Kotlin Weekly 中的数据..')
    # mkw_title, mkw_archive = get_kw_medium_act()
    # if mkw_archive:
    #     list_article.extend(get_kw_medium_data(mkw_archive))
    #     list_domain.append({'title': mkw_title, 'link': mkw_archive})

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
    download_data()
    # get_aw_data(url)
    # get_kw_archive('')

    # url = 'http://eepurl.com/dArA89'
    # url = 'https://us12.campaign-archive.com/?u=f39692e245b94f7fb693b6d82&id=ec3fe0b84f'
    # get_kw_data(url)

    # url = 'https://medium.com/mindorks/kotlin-weekly-update-47-bd993cb8751'
    # url = 'https://medium.com/p/bd993cb8751?source=user_profile---------4-------------------'
    # get_kw_medium_data(url)

    # get_kw_medium_act()
    print('end')
