import os
import logging
import threading
import fitz  # PyMuPDF
import re
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def clean_content(content, regex_pattern):
    # 删除匹配的内容
    content = re.sub(regex_pattern, '', content)

    return os.linesep.join([line for line in content.splitlines() if line.strip()])


def convert_and_clean_pdf(pdf_path, output_folder, regex_pattern):
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)

    # 创建一个文本文件的路径
    txt_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.txt'
    txt_path = os.path.join(output_folder, txt_filename)

    if os.path.exists(txt_path):  # Check if the file already exists
        print(f'文件已存在：{txt_filename}')
        return

    # 将PDF内容转换并清理
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            cleaned_text = clean_content(page.get_text(), regex_pattern)
            txt_file.write(cleaned_text)

    logging.info(f"已处理文件: {txt_filename}")

    # 关闭PDF文件
    pdf_document.close()


def process_pdfs_with_cleaning(pdf_folder, output_folder, regex_pattern=r'�|\(cid:\d+\)', max_workers=20):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [f for f in os.listdir(
        pdf_folder) if f.endswith('.pdf') | f.endswith('.PDF')]
    threads = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        thread = threading.Thread(target=convert_and_clean_pdf, args=(
            pdf_path, output_folder, regex_pattern))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    pdf_folder_path = r"E:\Downloads"
    output_folder_path = r"E:\Downloads"

    process_pdfs_with_cleaning(pdf_folder_path, output_folder_path)
    print("PDF文件已成功转换为文本文件并保存到目标文件夹。")
