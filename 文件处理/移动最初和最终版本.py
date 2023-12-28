import os
import shutil
from datetime import datetime


def organize_versions(input_folder):
    # 获取文件夹中的所有pdf文件
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

    # 根据前11个字符分组
    grouped_files = {}
    for pdf_file in pdf_files:
        prefix = pdf_file[:10]
        if prefix not in grouped_files:
            grouped_files[prefix] = []
        grouped_files[prefix].append(pdf_file)

    # 遍历每组文件，根据日期排序并移动到相应文件夹
    for prefix, files in grouped_files.items():
        sorted_files = sorted(
            files, key=lambda x: datetime.strptime(x[-14:-4], '%d-%m-%Y'))
        newest_file = sorted_files[-1]
        oldest_file = sorted_files[0]

        newest_folder = os.path.join(input_folder, "最新版本")
        oldest_folder = os.path.join(input_folder, "最旧版本")
        middle_folder = os.path.join(input_folder, "中间版本")

        for folder in [newest_folder, oldest_folder, middle_folder]:
            os.makedirs(folder, exist_ok=True)

        shutil.move(os.path.join(input_folder, newest_file),
                    os.path.join(newest_folder, newest_file))
        shutil.move(os.path.join(input_folder, oldest_file),
                    os.path.join(oldest_folder, oldest_file))

        for middle_file in sorted_files[1:-1]:
            shutil.move(os.path.join(input_folder, middle_file),
                        os.path.join(middle_folder, middle_file))


if __name__ == "__main__":
    input_folder = r""
    organize_versions(input_folder)
    print("文件整理完成。")
