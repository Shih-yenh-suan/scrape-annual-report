import os
import shutil
import PyPDF2
import concurrent.futures


def is_pdf_corrupted(file_path):
    try:
        with open(file_path, 'rb') as file:
            PyPDF2.PdfReader(file)
        return False
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return True


def move_corrupted_pdfs(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    def process_file(filename):
        filepath = os.path.join(source_folder, filename)
        destpath = os.path.join(destination_folder, filename)

        if filename.lower().endswith('.pdf'):
            if is_pdf_corrupted(filepath):
                print(f"Moving corrupted PDF: {filename}")
                shutil.move(filepath, destpath)
            else:
                print(f"PDF is not corrupted: {filename}")

    print("Starting PDF processing...")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        files = os.listdir(source_folder)
        executor.map(process_file, reversed(files))

    print("PDF processing completed.")


if __name__ == "__main__":
    input_folder = 'E:\\Downloads\\A股半年报'
    output_folder = 'E:\\Downloads\\A股半年报缺失出错2'

    move_corrupted_pdfs(input_folder, output_folder)
