from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import re
import shutil
from bs4 import BeautifulSoup


def process_html_files(filename):
    """ 处理文件夹中的HTML文件 """

    file_path = os.path.join(source_folder, filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        text = ' '.join(soup.stripped_strings)
        # 仅保留英文数字和简单标点
        # text = re.sub(r'[^a-zA-Z0-9.,ÝÞSR]+', '', text)
        text = re.sub(r'[\-\=\_\—\‑\s¨]+', '', text)
        text = text.upper()
        # print(text)
    match = re.search(
        r'(.{0,6})ANNUALREPORT.{0,10}SECTION13', text)
    if match and any(char in match.group(1) for char in chooiceList):
        print(f"{match.group(1)}: keep {filename[:18]}")
        return
    elif match:
        shutil.move(file_path, os.path.join(destination_folder, filename))
        print(f"{match.group(1)}: Moved {filename}")
    else:
        print(f"{filename}: not match")
        return


chooiceList = ["X", "Ý", "Þ", "☒", "☑", "■", "√", "⌧", "S", "Q", "×",
               "🗷,", "R", "M10", "M20", "✓", "20549", "", "Ÿ", "Ö", "Ü", "T"]
是否开启多线程 = 1
destination_folder = r"N:\Source_for_sale\美股年报\美股10-K和20-F年报文件\重复"
# 需要检索的特定字符列表


source_folder = r"N:\Source_for_sale\美股年报\美股10-K和20-F年报文件\2002"
if __name__ == "__main__":

    files = [filename for filename in os.listdir(
        source_folder) if filename.endswith('.html')]

    # 使用ProcessPoolExecutor来并行处理文件
    if 是否开启多线程 == 0:
        for i, filename in enumerate(files):
            process_html_files(filename, i, len(files))
    else:
        total_files = len(files)
        with ProcessPoolExecutor(max_workers=18) as executor:
            futures = {executor.submit(
                process_html_files, file): file for file in files}

            for i, future in enumerate(as_completed(futures)):
                file = futures[future]
                try:
                    future.result()  # 获取结果，如果有异常会在这里抛出
                except Exception as e:
                    print(f"Error processing file {file}: {e}")
                else:
                    progress = (i + 1) / total_files
                    print(f"Progress: {progress * 100:.2f}%")
