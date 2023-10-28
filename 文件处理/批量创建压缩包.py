import os
import zipfile
'''
输入：包含多个子文件夹的文件夹路径，压缩包的输出路径

将每个子文件夹分别进行压缩，同时打印出当前处理的文件

'''


def create_zip_for_each_subfolder(input_folder, output_folder):
    # 获取输入文件夹下的所有子文件夹
    subfolders = [f for f in os.listdir(
        input_folder) if os.path.isdir(os.path.join(input_folder, f))]

    # 遍历每个子文件夹并创建ZIP压缩包
    for folder in subfolders:
        folder_path = os.path.join(input_folder, folder)
        zip_filename = os.path.join(output_folder, f"{folder}.zip")

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 遍历子文件夹中的文件并将它们添加到ZIP压缩包
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    print(f"正在处理{file}：{zip_filename}")
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)


if __name__ == "__main__":
    input_folder = ""
    output_folder = input_folder

    if os.path.exists(input_folder) and os.path.isdir(input_folder) and os.path.exists(output_folder) and os.path.isdir(output_folder):
        create_zip_for_each_subfolder(input_folder, output_folder)
        print("已为每个子文件夹创建ZIP压缩包。")
    else:
        print("无效的文件夹路径。请确保输入的路径存在并且是一个文件夹。")
