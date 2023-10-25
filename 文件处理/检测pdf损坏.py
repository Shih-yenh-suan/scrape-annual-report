import os
import shutil
import PyPDF2
'''
输入文件夹 input_folder 和 output_folder
将 input_folder 中损坏的 pdf 文件移动到 output_folder
'''


def move_corrupted_pdfs(source_folder, destination_folder):
    # 检查目标文件夹是否存在，如果不存在则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        filepath = os.path.join(source_folder, filename)
        destpath = os.path.join(destination_folder, filename)

        # 检查文件是否为PDF
        if filename.lower().endswith('.pdf'):
            try:
                # 尝试打开PDF
                with open(filepath, 'rb') as file:
                    PyPDF2.PdfReader(file)
            except Exception:
                # 如果出现任何异常，都将PDF视为损坏，并移动到目标文件夹
                shutil.move(filepath, destpath)


if __name__ == "__main__":
    input_folder = 'E:\Downloads\上市公司报告位置\TXT文档\缺失出错'
    output_folder = 'E:\Downloads\上市公司报告位置\TXT文档\缺失出错2'

    move_corrupted_pdfs(input_folder, output_folder)
