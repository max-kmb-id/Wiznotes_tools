"""
Получение папок WizNote и списка заметок в каждой директории
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from wiz_client import WizNoteClient
from utils import list_folders_and_notes

def get_all_notes_in_folder(client, folder):
"""
Получение всех заметок из папки с обработкой случаев, когда их количество превышает 1000

Args:
client: Экземпляр WizNoteClient
folder: Путь к папке

Returns:
list: Список заметок без дубликатов
"""
try:
# Сначала получаем 1000 заметок (в порядке убывания, т.е. самые новые)
desc_notes = client.get_note_list(folder, max_notes=1000)

# Если получено 1000 заметок, возможно, их больше
if len(desc_notes) == 1000:
print(f"В папке {folder} более 1000 заметок; выполняется двусторонний запрос...")

# Получаем 1000 заметок в порядке возрастания (т.е. самые старые)
asc_notes = client._get_notes_with_order(folder, count=100, max_notes=1000, order="asc")

# Устраняем дубликаты по GUID
seen_guids = set()
all_notes = []

# Добавляем заметки из запроса по убыванию (самые новые)
for note in desc_notes:
guid = note.get('docGuid')
if guid and guid not in seen_guids:
all_notes.append(note)
seen_guids.add(guid)

# Добавляем заметки из запроса по возрастанию (самые старые, с проверкой на дубликаты)
new_notes_count = 0
for note in asc_notes:
guid = note.get('docGuid')
if guid and guid not in seen_guids:
all_notes.append(note)
seen_guids.add(guid)
new_notes_count += 1

total_unique = len(all_notes)
duplicate_count = len(desc_notes) + len(asc_notes) - total_unique

print(f"Папка {folder}: {len(desc_notes)} элементов (по убыванию) + {len(asc_notes)} элементов (по возрастанию), удалено дубликатов: {duplicate_count}, всего элементов: {total_unique}")

# Если после удаления дубликатов количество все еще близко к 2000, возможно, остались невыгруженные заметки
if total_unique >= 1800:
print(f"Предупреждение: папка {folder} может содержать более 2000 заметок; текущий метод не позволяет получить их все")

return all_notes
else:
# Менее 1000 элементов; return directly
return desc_notes

except Exception as e:
print(f"Ошибка при получении заметок для папки {folder}: {e}")
return []

def export_wiznotes_structure(config_path=None, export_notes=True):
"""
Экспорт структуры папок и списка заметок WizNote

Args:
config_path: Путь к файлу конфигурации; если None, читается из .env
export_notes: True — экспорт списка заметок; False — экспорт только структуры папок
"""
# Инициализация клиента
client = WizNoteClient(config_path)
client.login()

# Получение всех папок
folders = client.get_folders()

output_lines = []

if export_notes:
# Экспорт подробного списка заметок
total_notes = 0
folder_count = 0

for folder in folders:
folder_count += 1
try:
# Использование нового метода получения для обработки случаев с более чем 1000 заметок
notes = get_all_notes_in_folder(client, folder)
except Exception as e:
output_lines.append(f"Папка: {folder}  Ошибка получения заметок: {e}")
output_lines.append("")
continue
note_count = len(notes)
total_notes += note_count
output_lines.append(f"Папка: {folder}  Количество заметок: {note_count}")
for note in notes:
title = note.get('title', 'Без названия')
output_lines.append(f"    - {title}")
output_lines.append("")        output_lines.append(f"Всего папок: {folder_count}")
output_lines.append(f"Всего заметок: {total_notes}")

# Сохранение в файл
output_path = Path(__file__).parent / "output" / "folders & notes.txt"
output_filename = "folders & notes.txt"
else:
# Экспорт только структуры папок, одна запись на строку
for folder in folders:
output_lines.append(folder)

# Сохранение в файл
output_path = Path(__file__).parent / "output" / "WizNote_Directory.log"
output_filename = "WizNote_Directory.log"

# Убедиться, что выходная директория существует
output_path.parent.mkdir(parents=True, exist_ok=True)

# Сохранить файл
with open(output_path, 'w', encoding='utf-8') as f:
f.write('\n'.join(output_lines))

print(f"Информация сохранена в {output_path}")

if export_notes:
# Получить и вывести список всех папок
print("Все папки:")
list_folders_and_notes(client)

return output_path

if __name__ == "__main__":
# Экспорт только структуры папок
# export_wiznotes_structure(export_notes=False)

# Экспорт структуры папок и списка заметок
export_wiznotes_structure(export_notes=True)
