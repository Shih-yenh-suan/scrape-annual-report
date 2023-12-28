import os
import shutil

# 输入文件夹路径
folder_path = r""

# 遍历文件夹中的txt文件
for filename in os.listdir(folder_path):
    # 提取年份标记
    year = filename[7:11]

    # 创建对应年份的文件夹（如果不存在）
    year_folder = os.path.join(folder_path, year)
    if not os.path.exists(year_folder):
        os.mkdir(year_folder)

    # 构建源文件路径和目标文件路径
    source_file = os.path.join(folder_path, filename)
    target_file = os.path.join(year_folder, filename)

    # 移动文件到对应年份的文件夹
    shutil.move(source_file, target_file)
    print(year, filename)
print("文件移动完成")
