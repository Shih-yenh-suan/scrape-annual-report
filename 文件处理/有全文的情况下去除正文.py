import os
import shutil
from send2trash import send2trash


def remove_duplicate_files(folder_path):
    # 获取文件夹路径下所有文件的列表
    files = [f.path for f in os.scandir(folder_path) if f.is_file()]

    # 创建一个字典，用于存储每个文件标题对应的文件路径列表
    file_titles = {}

    # 遍历每个文件
    for file in files:
        # 获取文件名（不包括路径）
        file_name = os.path.basename(file)

        # 提取文件标题，即去除包含"_全文"或"_正文"的部分
        title = file_name.replace("全文", "").replace("正文", "")

        # 如果标题已经在字典中，将当前文件路径添加到对应的列表中
        if title in file_titles:
            file_titles[title].append(file)
        else:
            file_titles[title] = [file]

    # 遍历字典中的每个标题及其文件路径列表
    for title, file_list in file_titles.items():
        # 如果文件列表中包含"_全文"和"_正文"两种文件，删除"_正文"文件
        if len(file_list) == 2 and "全文" in file_list[0] and "正文" in file_list[1]:
            send2trash(file_list[1])


# 输入文件夹路径
folder_path = "E:\Downloads\A股三季报"

# 去重重复文件
remove_duplicate_files(folder_path)

print("文件去重完成！")
