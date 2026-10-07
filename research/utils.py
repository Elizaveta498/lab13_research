import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError


def sanitize_filename(name: str) -> str:
    
    name = os.path.basename(name)
    name = re.sub(r'[^A-Za-z0-9_.-]', '_', name)
    if not name.lower().endswith('.json'):
        name += '.json'
    unique = uuid.uuid4().hex[:8]
    return f"{unique}_{name}"


def get_data_dir() -> Path:
    
    return Path(settings.DATA_ROOT)


def save_records_to_file(records: list, filename: str = None) -> Path:
    
    if filename is None:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"research_{ts}_{uuid.uuid4().hex[:6]}.json"
    else:
        filename = sanitize_filename(filename)

    path = get_data_dir() / filename
    payload = {
        'exported_at': datetime.now().isoformat(),
        'count': len(records),
        'records': records,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def validate_research_record(record: dict, index: int = 0) -> dict:
    
    if not isinstance(record, dict):
        raise ValidationError(f'Запись #{index}: должна быть объектом.')

    required = ['title', 'author', 'field', 'description', 'start_date', 'status']
    for key in required:
        if key not in record or record[key] in (None, ''):
            raise ValidationError(f'Запись #{index}: отсутствует обязательное поле "{key}".')

    for date_field in ('start_date', 'end_date'):
        val = record.get(date_field)
        if val:
            try:
                datetime.strptime(val, '%Y-%m-%d')
            except (ValueError, TypeError):
                raise ValidationError(
                    f'Запись #{index}: неверный формат даты в "{date_field}" (нужен YYYY-MM-DD).'
                )

    if 'budget' in record and record['budget'] not in (None, ''):
        try:
            float(record['budget'])
        except (ValueError, TypeError):
            raise ValidationError(f'Запись #{index}: поле "budget" должно быть числом.')

    allowed_status = {'planned', 'ongoing', 'completed', 'published'}
    if record.get('status') not in allowed_status:
        raise ValidationError(
            f'Запись #{index}: недопустимый статус "{record.get("status")}".'
        )

    return record


def load_and_validate_json(path: Path) -> list:
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f'Файл не является валидным JSON: {e}')
    except OSError as e:
        raise ValidationError(f'Ошибка чтения файла: {e}')

    if isinstance(data, dict):
        if 'records' not in data or not isinstance(data['records'], list):
            raise ValidationError('В JSON-объекте отсутствует массив "records".')
        records = data['records']
    elif isinstance(data, list):
        records = data
    else:
        raise ValidationError('JSON должен быть объектом с полем "records" или массивом.')

    if not records:
        raise ValidationError('Файл не содержит записей.')

    return [validate_research_record(r, i + 1) for i, r in enumerate(records)]


def delete_file(path: Path):
    
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def list_data_files() -> list:
    
    data_dir = get_data_dir()
    if not data_dir.exists():
        return []
    files = []
    for p in sorted(data_dir.glob('*.json')):
        try:
            stat = p.stat()
            files.append({
                'name': p.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
            })
        except OSError:
            continue
    return files


def read_data_file(filename: str) -> dict:
    
    path = get_data_dir() / os.path.basename(filename)
    if not path.exists():
        raise ValidationError('Файл не найден.')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)