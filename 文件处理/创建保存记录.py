import os


def save_file_names_and_ids(folder_path):
    # 获取文件夹中的所有文件
    files = [file for file in os.listdir(
        folder_path) if os.path.isfile(os.path.join(folder_path, file))]

    # 提取文件名和前11个字符，保存到列表中
    file_names = [file for file in files]
    file_ids = [file[:11] for file in files]

    # 构造保存文件名和文件ID的文件路径
    file_names_path = os.path.join(folder_path, 'downloaded_files.txt')
    file_ids_path = os.path.join(folder_path, 'downloaded_id.txt')

    # 将文件名和文件ID写入对应的文件
    with open(file_names_path, 'w') as file_names_file:
        file_names_file.write('\n'.join(file_names))

    with open(file_ids_path, 'w') as file_ids_file:
        file_ids_file.write('\n'.join(file_ids))

    print(f"File names saved to: {file_names_path}")
    print(f"File IDs saved to: {file_ids_path}")


# 输入文件夹路径
folder_path = "E:\Source_for_sale\A股社会责任报告 PDF+TXT\A股社会责任报告TXT [12364份78.7GB]\附送：环境报告书TXT"

# 调用函数保存文件名和文件ID
save_file_names_and_ids(folder_path)
