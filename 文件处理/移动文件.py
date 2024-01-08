import os
import shutil


def move_files(source_folder, destination_folder):
    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)
        destination_path = os.path.join(destination_folder, filename)

        # 将文件移动到目标文件夹
        try:
            shutil.move(source_path, destination_path)
            print(f"Moved: {filename}")
        except Exception as e:
            print(f"Error moving {filename}: {e}")


# 输入源文件夹和目标文件夹路径
source_folder = "N:\Source_for_sale\美股年报补充文件"
destination_folder = "N:\Source_for_sale\美股报告10-K"

# 调用移动函数
move_files(source_folder, destination_folder)
