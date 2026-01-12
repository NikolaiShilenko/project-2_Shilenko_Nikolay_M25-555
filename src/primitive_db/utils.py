import json
import os

from .constants import DATA_DIR, META_FILE


def load_metadata(filepath=META_FILE):
    """Загружает метаданные из JSON-файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}


def save_metadata(data, filepath=META_FILE):
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_table_data(table_name):
    """Загружает данные таблицы из файла."""
    # Создаем директорию data, если её нет
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = f"{DATA_DIR}{table_name}.json"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы в файл."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = f"{DATA_DIR}{table_name}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
