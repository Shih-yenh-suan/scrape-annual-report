import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed


def format_date(date_str):
    """ 将日期字符串转换为 YYYY-MM-DD 格式 """
    try:
        return datetime.strptime(date_str, '%B%d,%Y').strftime('%Y-%m-%d')
    except Exception:
        return None


def extract_date_from_content(content):
    """ 提取内容中的日期并格式化 """
    match = re.search(
        r'annualreport.{0,15}section.*?for.{0,20}end(?:ed|ing)(\w*\d+,?\d{4})', content, re.IGNORECASE)
    if match:
        return match
    return None


def process_html_files(filename):
    """ 处理文件夹中的HTML文件 """
    with open(os.path.join(FOLDER, filename), 'r', encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')
        content = soup.get_text(separator=' ', strip=True)
        content = re.sub(r'[^a-zA-Z0-9.,]+', '', content)
        content = content.lower()
    file_date = filename.split('_')[1]
    content_date_row = extract_date_from_content(content)
    content_date = format_date(content_date_row.group(1))
    if content_date == None:
        print(f"{filename}: 文本中没有符合条件的日期")
        return
    matched_string = content_date_row.group(0)
    # 比对，上传日期必然在文本中日期的前面
    upload_date = filename.split('_')[-1][:10]
    upload_date_regulated = datetime.strptime(upload_date, "%Y-%m-%d")
    content_date_regulated = datetime.strptime(content_date, "%Y-%m-%d")
    if upload_date_regulated < content_date_regulated:
        print(f"上传日期{upload_date}小于文本日期{content_date}")
        return

    if content_date and file_date != content_date:
        print(matched_string)
        if 开启重命名 == 1:
            print(f"{file_date} vs {content_date}, 文件 {filename}")
            choice = input(f"是否改{filename}? (y/n): ")
            if choice.lower() == 'y':
                new_filename = filename.replace(
                    file_date, content_date)
            elif len(choice) == 10:
                new_filename = filename.replace(
                    file_date, choice)
            else:
                print(f"不修改文件名")
                return
            try:
                os.rename(os.path.join(FOLDER, filename),
                          os.path.join(FOLDER, new_filename))
            except FileExistsError:
                print(f"文件名已存在: {new_filename}")

            print(f"文件名已修改: {new_filename}")

        elif 开启重命名 == 0:
            try:
                shutil.move(os.path.join(FOLDER, filename),
                            os.path.join(correctTimeFolder, filename))
                print(f"文件 {filename} 已移动")
            except Exception as e:
                print(f"文件 {filename} 移动失败: {e}")
    else:
        print(f"{file_date} vs {content_date}, 文件 {filename}")


def main():
    if not os.path.exists(correctTimeFolder):
        os.mkdir(correctTimeFolder)
    files = [filename for filename in os.listdir(
        FOLDER) if filename.endswith('.html')]
    if 开启重命名 == 1:
        for filename in files:
            process_html_files(filename)
    elif 开启重命名 == 0:
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
                    print(
                        f"Progress: {(i+1)}/{total_files}, {(i+1)/total_files*100:.2f}%")
    else:
        print("输入错误")


开启重命名 = 1
correctTimeFolder = r"N:\Source_for_sale\美股年报\美股10-K和20-F年报文件\correctTimeFolder"
if 开启重命名 == 0:
    FOLDER = "N:\Source_for_sale\\美股年报\\美股10-K和20-F年报文件\\"
elif 开启重命名 == 1:
    FOLDER = correctTimeFolder


if __name__ == "__main__":
    main()
