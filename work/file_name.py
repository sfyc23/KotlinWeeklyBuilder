import os

def setup_download_dir(directory):
    """ 设置文件夹，文件夹名为传入的 directory 参数，若不存在会自动创建 """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            pass
    return True


def get_data_name(index):
    # '..'
    directory = os.path.join('file', 'data')
    setup_download_dir(directory)
    return os.path.join(directory,f'kotlin_weekly_{index}.json')

def get_markdown_name(index):
    directory = os.path.join('file', 'markdown')
    setup_download_dir(directory)
    return os.path.join(directory,f'kotlin_weekly_{index}.md')
