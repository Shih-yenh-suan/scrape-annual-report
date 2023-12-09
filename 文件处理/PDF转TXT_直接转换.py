import os
import logging
import threading
import fitz  # 这是PyMuPDF的导入语句
'''
输入 pdf 文件夹 pdf_folder_path 和 txt 文件夹 output_folder_path

使用 PyMuPDF 模块，将 pdf 转为 txt，
并使用多线程加速
'''


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def convert_pdf_to_text(pdf_path, output_folder):
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)

    # 创建一个文本文件的路径
    txt_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.txt'
    txt_path = os.path.join(output_folder, txt_filename)
    txt_path_check = os.path.join(output_folder, os.path.splitext(
        os.path.basename(txt_path))[0] + '.txt')
    if os.path.exists(txt_path_check):  # Check if the file already exists
        print(f'文件已存在：{txt_filename}')  # 设置进度条
        return
    # 打开文本文件以写入模式
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            txt_file.write(page.get_text())

    logging.info(f"已处理文件: {txt_filename}")

    # 关闭PDF文件
    pdf_document.close()


def process_pdfs(pdf_folder, output_folder, max_workers=20):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

    threads = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        thread = threading.Thread(
            target=convert_pdf_to_text, args=(pdf_path, output_folder))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    pdf_folder_path = r"E:\Downloads\A股社会责任报告"
    output_folder_path = r"E:\Downloads\A股社会责任报告"

    process_pdfs(pdf_folder_path, output_folder_path)
    print("PDF文件已成功转换为文本文件并保存到目标文件夹。")
