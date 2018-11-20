from work import weekly_read
from work import data_process
from work import markdown_builder
# from work import file_name
import time

if __name__ == '__main__':
    start_time = time.time()

    print(f'开始')

    index, data_file_name = weekly_read.download_data()

    data_process.clear_data(data_file_name)

    markdown_builder.builder(index, data_file_name)

    end_time = time.time()

    print(f'\n全部完成，全部用时:{end_time - start_time}秒')
