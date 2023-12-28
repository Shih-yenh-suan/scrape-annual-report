import os
import shutil
'''
输入文件夹路径A、B

比对文件夹A中各个文件，将前count_numbers个字符相同的文件移动到文件夹B中。

用于爬取完文件后，对重复的报告进行筛查
'''


def move_duplicate_files(source_folder, destination_folder):
    # 创建目标文件夹（如果不存在）
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹中的所有txt文件
    file_dict = {}
    for root, _, files in os.walk(source_folder):
        for file in files:
            prefix = file[:count_numbers]
            if prefix not in file_dict:
                file_dict[prefix] = []
            file_dict[prefix].append(os.path.join(root, file))

    # 移动重复文件
    for prefix, file_list in file_dict.items():
        if len(file_list) > 1:
            for file_path in file_list:
                # 移动文件到目标文件夹
                shutil.move(file_path, os.path.join(
                    destination_folder, os.path.basename(file_path)))
                print(
                    f"Moved {os.path.basename(file_path)} to {destination_folder}")


if __name__ == "__main__":
    input_folder = r''
    output_folder = r''
    count_numbers = 11

    move_duplicate_files(input_folder, output_folder)
