import os
import random
import shutil
'''
输入资源文件夹 source_folder 、目标文件夹 destination_folder 和抽取百分比 percentage

从资源文件夹随机抽取 percentage 的文件到目标文件夹中
'''


def copy_random_files(src_folder, dest_folder, percentage):
    # 获取源文件夹中的所有文件
    file_list = os.listdir(src_folder)

    # 计算要复制的文件数
    num_files_to_copy = int(len(file_list) * (percentage / 100))

    # 从文件列表中随机选择要复制的文件
    files_to_copy = random.sample(file_list, num_files_to_copy)

    # 确保目标文件夹存在
    os.makedirs(dest_folder, exist_ok=True)

    # 复制选定的文件到目标文件夹
    for file in files_to_copy:
        src_path = os.path.join(src_folder, file)
        dest_path = os.path.join(dest_folder, file)
        shutil.copy(src_path, dest_path)
        print(f'Copied: {file}')


if __name__ == "__main__":
    source_folder = r''
    destination_folder = '试看'
    percentage = float(input("请输入要复制的文件百分比（10% 输入 10）: "))

    copy_random_files(source_folder, destination_folder, percentage)
