
- Ввод данных о научных исследованиях через форму
- Валидация вводимых данных
- Сохранение записей в JSON-файлы
- Загрузка JSON-файлов с проверкой валидности
- Просмотр содержимого всех файлов
- Экспорт всех записей в один JSON
- Скачивание и удаление файлов



```bash
git clone <URL>
cd lab13_research

python -m venv venv
venv\Scripts\activate        


pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открыть: http://127.0.0.1:8000/

### Технологии
- Python 3.10+
- Django 5.x
- Bootstrap 5 (CDN)
- SQLite

### Формат JSON-файла

```json
{
  "records": [
    {
      "title": "Название исследования",
      "author": "Автор",
      "field": "Область науки",
      "description": "Описание",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD или null",
      "status": "planned|ongoing|completed|published",
      "budget": "число"
    }
  ]
}
```