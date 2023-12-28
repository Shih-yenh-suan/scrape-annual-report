import os
import shutil
import fitz  # PyMuPDF


def move_files_to_recycle_bin(folder_path):
    # 获取文件夹中的所有pdf文件
    pdf_files = [file for file in os.listdir(
        folder_path) if file.endswith(".pdf")]

    # 存储要移动到回收站的文件列表
    files_to_move = []

    # 遍历pdf文件
    for pdf_file in pdf_files:
        file_path = os.path.join(folder_path, pdf_file)

        # 获取文件名的前11个字符
        file_prefix = pdf_file[:11]

        # 获取PDF文件的页数和文件大小
        with fitz.open(file_path) as pdf_document:
            page_count = pdf_document.page_count
            file_size = os.path.getsize(file_path)

        # 在文件夹中查找具有相同前缀的其他pdf文件
        similar_files = [f for f in pdf_files if f.startswith(
            file_prefix) and f != pdf_file]

        # 对比页数和文件大小，保留页数或文件大小较大的一个，将其他添加到移动列表
        for similar_file in similar_files:
            similar_file_path = os.path.join(folder_path, similar_file)

            with fitz.open(similar_file_path) as similar_pdf:
                similar_page_count = similar_pdf.page_count
                similar_file_size = os.path.getsize(similar_file_path)

            # 如果当前文件页数或文件大小小于相似文件的页数或文件大小，添加到移动列表
            if page_count < similar_page_count or (page_count == similar_page_count and file_size < similar_file_size):
                files_to_move.append(file_path)
                break  # 只需添加一个相似文件到移动列表，因为其他相似文件将被处理到下一个循环

    # 将移动列表中的文件移动到回收站
    recycle_bin_path = os.path.join(folder_path, 'RecycleBin')
    os.makedirs(recycle_bin_path, exist_ok=True)

    for file_to_move in files_to_move:
        recycled_file_path = os.path.join(
            recycle_bin_path, os.path.basename(file_to_move))
        shutil.move(file_to_move, recycled_file_path)
        print(f"Moved {os.path.basename(file_to_move)} to RecycleBin")


folder_path_A = r""

# 调用函数移动文件到回收站
move_files_to_recycle_bin(folder_path_A)
