from lxml import etree
import os
import re
import requests
from Config import *
from concurrent.futures import ThreadPoolExecutor
from functools import partial


def get_charset(file_path):
    with open(file_path, 'rb') as file:
        # 读取文件的前一部分来寻找charset
        content_head = file.read(1024).decode('ascii', errors='ignore')
        charset_match = re.search(
            r'charset=["\']?([\w-]+)', content_head, re.IGNORECASE)
        return charset_match.group(1) if charset_match else 'utf-8'


def process_file(file_path):
    print(file_path)
    charset = get_charset(file_path)

    date_in_filename = os.path.basename(file_path)[-10:]  # Extract date string
    date_components = date_in_filename.split('-')
    date_formatted = f"{date_components[2]}/{date_components[1]}{date_components[0]}"

    with open(file_path, 'r', encoding=charset, errors='ignore') as file:
        content = file.read()

        subfolder_path = os.path.join(save_folder, os.path.basename(file_path))
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)

        html_tree = etree.HTML(content)
        links = html_tree.xpath('//a[@target="_blank"]')

        for i, link in enumerate(links):
            href = link.get('href')
            name = link.xpath('string(.)').strip()

            if href:
                pdf_link = f'https://www1.hkexnews.hk/listedco/listconews/sehk/{date_formatted}/{href}'
                pdf_filename = os.path.join(
                    subfolder_path, f'{os.path.basename(file_path)}_{i}_{name}.pdf')

                # Check if the PDF file already exists, if so, skip
                if os.path.exists(pdf_filename):
                    print(
                        f'{os.path.basename(file_path)}_{i}_{name}.pdf already exists. Skipping...')
                    continue

                pdf_response = requests.get(pdf_link, headers=HEADERS)
                pdf_response.raise_for_status()

                with open(pdf_filename, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)
                print(f'{os.path.basename(file_path)}_{i}_{name}.pdf downloaded')


def download_pdfs_multithreaded(folder_path):
    files = [os.path.join(folder_path, filename)
             for filename in os.listdir(folder_path)]

    with ThreadPoolExecutor() as executor:
        executor.map(process_file, files)


# Example usage
save_folder = r"E:\Downloads\港股年报\港股年报"
download_pdfs_multithreaded(r'E:\Downloads\港股年报\港股年报')
