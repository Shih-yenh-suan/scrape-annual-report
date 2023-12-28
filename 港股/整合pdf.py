import os
from PyPDF2 import PdfMerger


def merge_pdfs(folder_path):
    # 获取文件夹下的所有子文件夹
    subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]

    for subfolder in subfolders:
        pdf_files = [f.path for f in os.scandir(
            subfolder) if f.is_file() and f.name.endswith('.pdf')]

        if pdf_files:
            # 按标题顺序排序PDF文件
            pdf_files.sort(key=lambda x: get_pdf_title(x))

            # 创建一个PDF合并对象
            pdf_merger = PdfMerger()

            # 将PDF文件逐个添加到合并对象
            for pdf_file in pdf_files:
                pdf_merger.append(pdf_file)

            # 合并后的PDF文件保存路径
            output_path = os.path.join(
                folder_path, os.path.basename(subfolder) + '.pdf')

            # 写入合并后的PDF文件
            with open(output_path, 'wb') as output_pdf:
                pdf_merger.write(output_pdf)

            print(
                f'Merged PDFs for {os.path.basename(subfolder)} saved to {output_path}')


def get_pdf_title(pdf_path):
    # 读取PDF文件的标题信息（这里简化为取文件名）
    return os.path.basename(pdf_path)


# 输入文件夹路径
folder_path = r""

# 调用函数进行PDF合并
merge_pdfs(folder_path)
