import json
from work import file_name


def builder(index, data_file_name):

    print('\n第 3 部分：开始生成 markDown ')
    markdown_file_name = file_name.get_markdown_name(index)
    with open(data_file_name, 'r', encoding='utf-8') as file:
        dict_data = json.loads(file.read())

    list_article = dict_data['data']
    list_domain = dict_data['domain']
    list_about_me = [
        {'title': '微博', 'link': 'https://weibo.com/sfyc23'},
        {'title': '简书', 'link': 'https://www.jianshu.com/u/6e8801f536bb'},
        {'title': '掘金', 'link': 'https://juejin.im/user/574cfe16c4c97100549a50c5'},
        {'title': 'Github', 'link': 'https://github.com/sfyc23'}
    ]

    # [链接描述文字（可见）](链接地址)
    with open(markdown_file_name, 'w+', encoding='utf-8') as file:
        # # 生成标题文字
        file.write('Kotlin Weekly 中文周报\n\n---\n\n')

        # 文章主要内容生成
        for i, acticle in enumerate(list_article):
            title = f"{i + 1}. [{acticle['title']}]({acticle['link']}) ({acticle['domain']})  "
            trans_title = f"{acticle['trans_title']}"

            brief = f"{acticle['brief']}"
            trans_brief = f"{acticle['trans_brief']}"
            content = '  \n'.join([title, trans_title, brief, trans_brief])
            file.write(content)
            file.write('\n\n')

        # 文章来源说明
        file.write('---\n\n文章主要来源:\n')
        for i, domain in enumerate(list_domain):
            file.write(f"{i+1}. [{domain['title']}]({domain['link']})  \n")
        file.write('\n---\n\n')

        # 关于我
        file.write('关于我：')
        list_write = []
        for i, domain in enumerate(list_about_me):
            list_write.append(f"[{domain['title']}]({domain['link']})")
        file.write('，'.join(list_write))
        file.write('。  \n\n---')

    print('Markdown 已生成')
