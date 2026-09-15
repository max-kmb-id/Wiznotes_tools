"""
Чтение данных из WizNote и экспорт заметок (по отдельности или пакетами)
"""

import sys
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Импорт модулей
from export_wiznotes.wiz_client import WizNoteClient
from export_wiznotes.note_exporter import NoteExporter
from export_wiznotes.utils import setup_logging, list_folders_and_notes


def read_folders_from_log(log_file):
"""Чтение списка папок из файла журнала"""
folders = []
with open(log_file, 'r', encoding='utf-8') as f:
for line in f:
folder = line.strip()
if folder and not folder.startswith('#'):
folders.append(folder)
return folders


def export_folder(args):
"""Экспорт заметок из одной папки"""
folder, client, export_dir, max_notes, reexport_dot_files = args
try:
exporter = NoteExporter(client)
logging.info(f"Начало экспорта папки: {folder}")
exporter.export_notes(
folder=folder,
export_dir=export_dir,
max_notes=max_notes,
resume=True,
reexport_dot_files=reexport_dot_files
)
logging.info(f"Экспорт папки завершен: {folder}")
return True
except Exception as e:
logging.error(f"Ошибка при экспорте папки {folder}: {e}")
return False


def main():
"""Основная функция"""
# ========== Параметры конфигурации ==========
# Базовая конфигурация (данные учетной записи считываются из файла .env в корне проекта; см. .env.example)
export_dir = Path.cwd() / "export_wiznotes" / "output"
max_notes = None  # Без ограничения количества заметок; автоматическая обработка случаев с >1000 заметок (через двунаправленный запрос и дедупликацию)
log_file = export_dir / "为知笔记目录.log"

# Опция восстановления: нужно ли повторно экспортировать файлы, в именах которых есть символ "." (используется для исправления проблем, возникших при предыдущем экспорте)
#    # Установите значение True, если при предыдущем экспорте возникали проблемы с обрезанием имен файлов; в обычном режиме установите False
reexport_dot_files = False  # Установите True для исправления проблем предыдущего экспорта

# Настройка производительности
max_workers = 10  # Количество потоков для параллельной загрузки

try:
# Настройка логирования
setup_logging(export_dir)

# Создание клиента и вход в систему (конфигурация учетной записи считывается из файла .env)
client = WizNoteClient()
client.login()

# Чтение списка папок
folders = read_folders_from_log(log_file)
logging.info(f"Всего считано папок: {len(folders)}")

if reexport_dot_files:
logging.info("Включен режим повторного экспорта для папок с точкой в ​​названии; исправление проблем предыдущего экспорта")

# Подготовка аргументов для экспорта
export_args = [(folder, client, export_dir, max_notes, reexport_dot_files) for folder in folders]

# Использование пула потоков для параллельного экспорта
with ThreadPoolExecutor(max_workers=max_workers) as executor:
# Постановка задач в очередь
future_to_folder = {
executor.submit(export_folder, export_arg): export_arg[0]
for export_arg in export_args
}

# Обработка завершенных задач
success_count = 0
for future in as_completed(future_to_folder):
folder = future_to_folder[future]
try:
if future.result():
success_count += 1
except Exception as e:
logging.error(f"Ошибка при обработке папки {folder}: {e}")

logging.info(f"Экспорт завершен; успешно экспортировано папок: {success_count}/{len(folders)}")

except KeyboardInterrupt:
logging.info("Программа остановлена ​​пользователем")
sys.exit(0)
except Exception as e:
logging.error(f"Ошибка выполнения программы: {e}")


if __name__ == '__main__':
main()
