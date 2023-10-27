import os
import shutil
'''
输入文件夹路径A、B、C、判断字符数

比对文件夹A和B中各个文件前count_numbers个字符，将A中有而B中没有的文件移动到路径C

用于在对pdf文本进行OCR识别，删除识别失败的txt文本后，
输入pdf文件夹A和txt文件夹B，
从而将未能成功匹配的pdf文件筛选出来
'''


# 输入文件夹A和文件夹B的路径
folder_a_path = r"E:\Source_for_sale\A股年报 PDF+TXT\A股年报PDF [56081份159GB]"
folder_b_path = r"E:\Source_for_sale\A股年报 PDF+TXT\A股年报TXT [56081份18.8GB]"
folder_c_path = r"E:\Source_for_sale\A股年报 PDF+TXT\A"  # 新文件夹C的路径
count_numbers = 11

# 确保文件夹C存在，如果不存在则创建
if not os.path.exists(folder_c_path):
    os.makedirs(folder_c_path)

# 获取文件夹A中的文件名前count_numbers个字符的列表
folder_a_files = {filename[:count_numbers]
                  for filename in os.listdir(folder_a_path)}

# 获取文件夹B中的文件名前count_numbers个字符的列表
folder_b_files = {filename[:count_numbers]
                  for filename in os.listdir(folder_b_path)}

# 找出在文件夹A中有而文件夹B中没有的文件（根据前count_numbers个字符的文件名）
new_files = folder_a_files - folder_b_files

# 遍历新文件列表，使用完整文件名进行移动操作
for filename_prefix in new_files:
    source_file = os.path.join(folder_a_path, [filename for filename in os.listdir(
        folder_a_path) if filename.startswith(filename_prefix)][0])
    destination_file = os.path.join(folder_c_path, [filename for filename in os.listdir(
        folder_a_path) if filename.startswith(filename_prefix)][0])
    shutil.copy(source_file, destination_file)

print("文件比对完成，新文件已复制到文件夹C中。")
