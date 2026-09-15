"""Пакетное преобразование устаревших файлов WizNote формата `.md.ziw` в стандартные файлы Markdown.
WizNote поддерживает экспорт заметок в формат Markdown только по одной; данный скрипт автоматически находит заметки, созданные в формате Markdown, в папке с данными старой версии WizNote и выполняет их пакетный экспорт в виде стандартных файлов Markdown.
"""
import pathlib
import zipfile
import shutil
from lxml import etree


def get_markdown_files(data_path):
    """Получить список файлов .md.ziw"""
    md_files = list(data_path.glob('**/*.md*.ziw'))
    print(f'Всего найдено{len(md_files)} Markdown-файл.')
    return md_files


def ziw2md(md_file, export_md_path, tmp_path, abs_img_path=False):
    """Преобразуйте файлы .md.ziw в стандартные файлы .md и экспортируйте изображения и вложения в локальную директорию."""
    ziw_zip = zipfile.ZipFile(md_file)
    ziw_zip.extractall(tmp_path)
    ziw_zip.close()

    print(f"Преобразование...《{md_file.stem}》……")
    export_md_file = export_md_path.joinpath(md_file.parent.stem, md_file.stem.replace('.md', '')+'.md')
    export_attachment_path = export_md_file.parent / export_md_file.stem   # Директория для сохранения изображений и вложений

    with open(tmp_path / 'index.html', encoding='utf-16') as f1:
        content = f1.read()
        content = content.replace('</div>', '\n')
        content = content.replace('<br>', '\n')
        content = content.replace('<br/>', '\n')
        '''
        pattern1 = re.compile(r'<!doctype.*?</head>', re.DOTALL | re.IGNORECASE | re.MULTILINE)
        content = pattern1.sub('', content)
        pattern2 = re.compile(r'.*WizHtmlContentBegin-->', re.DOTALL | re.IGNORECASE | re.MULTILINE)
        content = pattern2.sub('', content)
        content = re.sub(r'<body.*?>', '', content)
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        content = content.replace('&nbsp;', ' ')
        content = content.replace('<div>', '')
        content = content.replace('</div>', '\n')
        content = content.replace('<br/>', '\n')
        content = content.replace('<br>', '\n')
        content = content.replace('</body></html>', '')
        # content = html2text.html2text(content)
        content = content.replace(r'\---', '---').strip()
        content = re.sub(r'<ed_tag name="markdownimage" .*?</ed_tag>', '', content).strip()   # Замените содержимое в конце текста, содержащее файлы со ссылками на изображения.
        '''
        tree = etree.HTML(content)
        content = tree.xpath('//body')[0].xpath('string(.)')

        # Измените ссылки на файлы изображений, указав соответствующие директории.
        if abs_img_path:
            content = content.replace('index_files', str(export_attachment_path))
        else:
            content = content.replace('index_files', export_attachment_path.stem)

    # Вывод Markdown-файлов, упорядоченных по каталогам
    if not (export_md_path / md_file.parent.stem).exists():
        (export_md_path / md_file.parent.stem).mkdir()
    with open(export_md_file, 'w', encoding='utf-8') as f2:
        f2.write(content)
    print(f'已导出：{export_md_file}。')

    # Скопируйте файлы изображений из каталога `index_files` в каталог, названный в честь заголовка Markdown-файла.
    if (tmp_path / 'index_files').exists():
        # shutil.copytree((tmp_path / 'index_files'), export_attachment_path, dirs_exist_ok=True)
        (tmp_path / 'index_files').rename(export_attachment_path)

    # Скопируйте файлы из каталога вложений в каталог, названный в честь заголовка Markdown-файла.
    attachment_path = md_file.parent.joinpath(md_file.stem, '.md_Attachments')
    if attachment_path.exists():
        if not export_attachment_path.exists():
            export_attachment_path.mkdir()
        for attachment in attachment_path.glob('*.*'):
            shutil.copy2(attachment, export_attachment_path)
    # shutil.rmtree(tmp_path)


if __name__ == "__main__":
    wizdata_path = pathlib.Path(r'C:\QMDownload\Backup\Wiz Knowledge\Data\quincy.zou@gmail.com')
    export_md_path = pathlib.Path(r'C:\QMDownload\Backup\Wiz Knowledge\exported_md')
    tmp_path = export_md_path / 'temp'

    keyword = 'Проблемы и решения'

    md_files = get_markdown_files(wizdata_path)
    for md_file in md_files:
        # Экспортировать все файлы Markdown
        if not keyword:
            ziw2md(md_file, export_md_path, tmp_path, abs_img_path=False)
        # Экспортировать только те файлы Markdown, в именах которых содержится указанное ключевое слово.
        elif keyword in md_file.stem:
            ziw2md(md_file, export_md_path, tmp_path, abs_img_path=False)
