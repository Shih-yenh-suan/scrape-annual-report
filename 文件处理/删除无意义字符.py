import os
import re
from concurrent.futures import ThreadPoolExecutor


def clean_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    # 删除空白行
    lines = [line for line in lines if line.strip()]

    # 删除乱码
    lines = [re.sub(r'[^\x00-\x7F]+', '', line) for line in lines]

    # 删除形如“(cid:数字)”的内容
    lines = [re.sub(r'\(cid:\d+\)', '', line) for line in lines]

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    print(f"处理完成: {file_path}")


def clean_folder(folder_path):
    # 获取文件夹中的所有txt文件
    txt_files = [file for file in os.listdir(
        folder_path) if file.endswith('.txt')]

    with ThreadPoolExecutor(max_workers=20) as executor:  # 设置线程池最大工作线程数
        executor.map(clean_file_content, [os.path.join(
            folder_path, txt_file) for txt_file in txt_files])


if __name__ == "__main__":
    # 获取文件夹路径输入
    folder_path = r"E:\Downloads\港股年报\港股年报英文版TXT"

    # 处理文件夹中的所有txt文件
    clean_folder(folder_path)

    print("处理完成！")
