import os
import shutil


def move_10ka_files(input_folder, output_folder):
    # 确保目标文件夹存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取输入文件夹中所有文件列表
    files = os.listdir(input_folder)

    # 遍历文件列表
    for file_name in files:
        # 解析文件名，提取类型信息
        file_name_parts = file_name.split('_')

        # 检查是否有足够的部分来解包
        if len(file_name_parts) >= 6:
            _, _, _, _, file_type, _ = file_name_parts

            # 如果文件类型为 "10-K"，则移动文件到目标文件夹
            if file_type != "10-KA" and file_type != "20-FA":
                source_path = os.path.join(input_folder, file_name)
                destination_path = os.path.join(output_folder, file_name)
                shutil.move(source_path, destination_path)
                print(f"Moved {file_name} to {output_folder}")
        else:
            print(f"Invalid file name format: {file_name}")


# 指定输入和输出文件夹路径
input_folder_path = r""
output_folder_path = r""

# 调用函数进行移动操作
move_10ka_files(input_folder_path, output_folder_path)
