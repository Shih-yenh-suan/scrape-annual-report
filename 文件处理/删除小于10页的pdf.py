import os
import send2trash
import PyPDF2
'''
输入文件夹路径 folder_path 和页面限制 pdf_pages_limit

将路径下少于 pdf_pages_limit 页的pdf移动到回收站。
'''


def count_pdf_pages(pdf_path):
    # 打开PDF文件
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # 获取PDF文件的页数
        return len(pdf_reader.pages)


def main():

    # 遍历文件夹中的文件
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                page_count = count_pdf_pages(pdf_path)

                # 如果页数少于 pdf_pages_limit 页，则移动到回收站
                if page_count <= pdf_pages_limit:
                    print(f"移动文件到回收站: {pdf_path}")
                    send2trash.send2trash(pdf_path)

    print("任务完成")


folder_path = r""
pdf_pages_limit = 10


if __name__ == "__main__":
    main()
