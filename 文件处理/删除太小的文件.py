import os


def delete_small_files(folder_path, size_limit_kb):
    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            # 获取文件大小，以KB为单位
            file_size_kb = os.path.getsize(file_path) / 1024

            # 如果文件大小小于指定限制，删除文件
            if file_size_kb <= size_limit_kb:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")


# 输入文件夹路径和文件大小限制（以KB为单位）
folder_path = r"N:\Source_for_sale\美股年报\报告文件"
size_limit_kb = float(1)

# 调用删除函数
delete_small_files(folder_path, size_limit_kb)
