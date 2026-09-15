"""Создавать шаблоны ежемесячных журналов"""
import pathlib
from datetime import date, datetime
import calendar


year = 2026
path = pathlib.Path.cwd() / 'diaries'
template = path / 'diary_template.md'

with open(template, encoding='utf-8') as f:
    lines = f.readlines()
    base_content = ''.join(lines[1:])

for month in range(1, 13):
    day_count = calendar.monthrange(year, month)[1]
    month_content = f'# {year}Год{month}Ежемесячный дневник\n\n'
    for day in range(1, day_count+1):
        today = date(year, month, day)
        first_line = f"## {today} {datetime.strftime(today, '%A')[:3]} прозрачный\n"
        content = first_line + base_content + '\n\n'
        month_content += content

    with open(path / f'{year}-{month:0>2d}.md', 'w', encoding='utf-8') as f:
        f.write(month_content)

print(f"Уже участвую{path.absolute()}Сгенерировать в директории{year}Шаблон ежедневника (годовой/месячный)。")
