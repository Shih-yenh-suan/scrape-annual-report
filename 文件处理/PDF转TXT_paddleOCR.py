import os
import fitz  # PyMuPDF
import tempfile
from paddleocr import PaddleOCR
import logging
from multiprocessing import Pool
'''
输入 pdf 文件夹 pdf_folder_path 和 txt 文件夹 output_folder_path

使用 PyMuPDF 模块，首先将pdf的每一页转换为图片，保存在 tempfile 中，
然后使用 paddleocr 模块，将 这些图片 转为 txt 并合并为一个文件，
同时使用多进程加速
'''


def process_page(pdf_file_path, page_num, txt_file_path):
    '''
    实现页面识别功能
    输入 pdf 文件夹路径， 页面数量 page_num ， txt 文件夹路径
    输出页面数量， txt 内容
    '''
    logging.getLogger('ppocr').setLevel(logging.ERROR)

    doc = fitz.open(pdf_file_path)  # 在每个子进程中重新打开PDF文件
    pdf_file = os.path.basename(pdf_file_path)

    print(f"开始处理 {pdf_file}, 页面 {page_num + 1}/{doc.page_count}")  # 开始处理时的输出

    try:
        # 创建一个新的 PaddleOCR 实例
        ocr = PaddleOCR(use_angle_cls=True)

        # 将PDF的每一页转换为图片
        page = doc.load_page(page_num)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as temp_file:
            pix = page.get_pixmap()
            pix.save(temp_file.name)

            # 对每一页进行OCR处理
            result = ocr.ocr(temp_file.name, cls=True)

            txt_content = ''
            for line in result:
                if line is None:
                    continue
                txt_content += ' '.join(
                    [word_info[1][0] if isinstance(word_info[1], tuple)
                     else word_info[1] for word_info in line]) + '\n'

        # 完成处理时的输出
        print(f"已完成 {pdf_file}, 页面 {page_num + 1}/{doc.page_count}")

        return page_num, txt_content

    except Exception as e:
        print(f"处理错误 {pdf_file}, 页面 {page_num + 1}/{doc.page_count}: {e}")
        return page_num, None


def process_pdf(pdf_path, output_folder, core_count):
    '''
    在对单个 pdf 进行转换时，实现多进程功能
    输入 pdf 文件夹路径， 输出文件夹 output_folder ，核心数 core_count
    '''
    logging.getLogger('ppocr').setLevel(logging.ERROR)
    pool = Pool(processes=core_count)

    doc = fitz.open(pdf_path)
    pdf_file = os.path.basename(pdf_path)

    # 检查是否已存在相应的txt文件
    txt_file_path = os.path.join(
        output_folder, pdf_file.replace('.pdf', '.txt'))
    if os.path.exists(txt_file_path):
        print(f"{txt_file_path} 已存在，跳过")
        return

    # 使用进程池并发处理PDF中的页面
    with Pool() as pool:
        results = pool.starmap(
            process_page, [(pdf_path, page_num, txt_file_path)
                           for page_num in range(doc.page_count)])

    # 按页面顺序写入文本文件
    results.sort()
    with open(txt_file_path, 'a', encoding='utf-8') as txt_file:
        for _, txt_content in results:
            if txt_content is not None:
                txt_file.write(txt_content)

    print(f"{pdf_file} 已转换完成")


def pdf_to_txt(input_folder, output_folder):
    '''
    顺序对 pdf 处理。
    输入 pdf 文件夹路径 input_folder 和输出文件夹 output_folder
    执行 process_pdf 功能。
    '''
    # 如果输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取指定文件夹下的所有PDF文件
    pdf_files = [os.path.join(input_folder, f)
                 for f in os.listdir(input_folder)
                 if f.endswith('.pdf')]

    for pdf_file in pdf_files:
        process_pdf(pdf_file, output_folder, 5)


if __name__ == "__main__":
    pdf_folder_path = "E:\Source_for_sale\A股年报 PDF+TXT\A股年报PDF，无法识别，采用OCR - 副本"
    output_folder_path = "E:\Source_for_sale\A股年报 PDF+TXT\A股年报PDF，无法识别，采用OCR - 副本"

    pdf_to_txt(pdf_folder_path, output_folder_path)
    print("PDF文件已成功转换为文本文件并保存到目标文件夹。")
