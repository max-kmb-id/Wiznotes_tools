"""Найдите файлы, которые не удалось загрузить в WizNote, и переместите их обратно в папку для файлов, ожидающих загрузки."""
import shutil
import os
import re


def process(text):
    """Обработайте исходные имена файлов, чтобы упростить их сравнение с именами файлов Wiz."""
    text = re.sub(r'_\d.ziw', '', text)
    # match_obj = re.match(r'(.*?)#', text)
    # if match_obj:
    #     text = match_obj.group(1)

    replace_words = ['.ziw','.jpg','.png', '.webp', '.svg', '.jpeg', '#', '-', ',', '%',"'", '_', ' ']
    for word in replace_words:
        text = text.replace(word, '')
    text = text.strip()

    return text[:30]


def get_undone_files(wiz_path, img_done_path):
    """Извлеките изображения и соответствующие текстовые файлы OCR, которые не удалось импортировать в WizNote."""
    wiz_files = [file for file in os.listdir(wiz_path) if file.endswith('.ziw')]
    wiz_files_processed = [process(file) for file in wiz_files]
    img_done_files = [file for file in os.listdir(img_done_path) if (file.endswith('.jpg') or file.endswith('.png'))]   # Отправлены изображения (на самом деле некоторые изображения не удалось загрузить в WizNote)

    # Если имя файла из числа обработанных изображений не найдено в каталоге WizNote, передача считается неудачной.
    img_undone_files = []
    for file in img_done_files:
        if process(file) not in wiz_files_processed:
            img_undone_files.append(os.path.join(img_done_path, file))
    txt_undone_files = [file[:-4]+'.txt' for file in img_undone_files]

    print(len(img_undone_files))
    print('\n'.join(img_undone_files))

    return img_undone_files, txt_undone_files


def move_undone_files(img_undone_files, txt_undone_files, todo_path):
    """Переместите изображения и текстовые файлы, которые не удалось захватить, в папку для объектов, ожидающих обработки."""
    for img in img_undone_files:
        shutil.move(img, todo_path)
    for txt in txt_undone_files:
        shutil.move(txt, todo_path)


if __name__ == "__main__":
    wiz_path = r'C:\QMDownload\Backup\Wiz Knowledge\Data\quincy.zou@gmail.com\Крупицы знаний | Мышление и письмо | Заметки в инфографике'
    img_done_path = r'C:\QMDownload\BaiduNet\mate30\done'
    todo_path = r'C:\QMDownload\BaiduNet\mate30'

    img_undone_files, txt_undone_files = get_undone_files(wiz_path, img_done_path)
    move_undone_files(img_undone_files, txt_undone_files, todo_path)
