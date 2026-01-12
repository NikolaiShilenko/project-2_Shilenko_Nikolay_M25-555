def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных."""
    # Проверка существования таблицы
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    # Проверка типов столбцов
    valid_types = {"int", "str", "bool"}
    table_columns = []

    # Добавляем автоматический столбец ID
    table_columns.append("ID:int")

    for column in columns:
        if ':' not in column:
            print(f'Некорректный формат столбца: {column}')
            return metadata

        col_name, col_type = column.split(':', 1)
        if col_type not in valid_types:
            print(f'Некорректный тип данных: {col_type}. Допустимые: int, str, bool')
            return metadata

        table_columns.append(f"{col_name}:{col_type}")

    # Сохраняем таблицу в метаданные
    metadata[table_name] = table_columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(table_columns)}')
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Выводит список всех таблиц."""
    if not metadata:
        print("Нет созданных таблиц.")
        return

    for table_name in metadata:
        print(f"- {table_name}")
