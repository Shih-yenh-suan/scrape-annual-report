import os


def save_file_names_and_ids(folder_path, txt_path):
    file_names = []
    file_ids = []

    # 遍历文件夹及其所有子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 提取文件名和前11个字符，保存到列表中
            file_names.append(file)
            file_ids.append(file[:10])

    # 构造保存文件名和文件ID的文件路径
    file_names_path = os.path.join(txt_path, 'downloaded_files.txt')
    file_ids_path = os.path.join(txt_path, 'downloaded_id.txt')

    # 将文件名和文件ID写入对应的文件
    with open(file_names_path, 'w', encoding='utf-8') as file_names_file:
        file_names_file.write('\n'.join(file_names))

    with open(file_ids_path, 'w', encoding='utf-8') as file_ids_file:
        file_ids_file.write('\n'.join(file_ids))

    print(f"File names saved to: {file_names_path}")
    print(f"File IDs saved to: {file_ids_path}")


# 输入文件夹路径
folder_path = r"E:\Source_for_sale\港股年报【中27202】【英27172】\港股年报中文版TXT"
txt_path = folder_path
# 调用函数保存文件名和文件ID
save_file_names_and_ids(folder_path, txt_path)
