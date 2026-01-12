from .utils import load_table_data, save_table_data


def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

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

    metadata[table_name] = table_columns
    print(f'Таблица "{table_name}" успешно создана'
          f' со столбцами: {", ".join(table_columns)}')

    # пустой файл данных для таблицы
    save_table_data(table_name, [])

    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    # Удаляем файл с данными таблицы если онесть
    try:
        import os
        os.remove(f"data/{table_name}.json")
    except FileNotFoundError:
        pass

    return metadata


def list_tables(metadata):
    """Выводит список всех таблиц."""
    if not metadata:
        print("Нет созданных таблиц.")
        return

    for table_name in metadata:
        print(f"- {table_name}")


def _convert_value(value_str, col_type):
    """Преобразует строковое значение в нужный тип."""
    if col_type == "int":
        return int(value_str)
    elif col_type == "bool":
        if value_str.lower() == "true":
            return True
        elif value_str.lower() == "false":
            return False
        else:
            raise ValueError(f"Некорректное булево значение: {value_str}")
    else:  # str
        # удалить кавычки если они есть
        if (value_str.startswith('"') and value_str.endswith('"')) or \
                (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        return value_str


def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    # загрузить данные таблицы
    table_data = load_table_data(table_name)

    # получаем схему столбцов (без id)
    columns_schema = metadata[table_name][1:]  # Пропускаем ID:int

    # Проверяем количество значений
    if len(values) != len(columns_schema):
        print(f'Ошибка: Ожидается {len(columns_schema)} значений,'
              f' получено {len(values)}')
        return None

    # Генерим новый ID
    if table_data:
        max_id = max(row["ID"] for row in table_data)
        new_id = max_id + 1
    else:
        new_id = 1

    # Создаем новую запись
    new_row = {"ID": new_id}

    # Добавить значения с проверкой типов
    for i, col_schema in enumerate(columns_schema):
        col_name, col_type = col_schema.split(":")
        try:
            converted_value = _convert_value(values[i], col_type)
            new_row[col_name] = converted_value
        except (ValueError, TypeError) as e:
            print(f'Ошибка преобразования типа для столбца {col_name}: {e}')
            return None

    # запись в данные
    table_data.append(new_row)

    # сохраняем данные
    save_table_data(table_name, table_data)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_name, where_clause=None):
    """Выбирает записи из таблицы."""
    table_data = load_table_data(table_name)

    if not where_clause:
        return table_data

    # фильтр по условию
    filtered_data = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if str(row.get(col)) != str(val):
                match = False
                break
        if match:
            filtered_data.append(row)

    return filtered_data


def update(metadata, table_name, set_clause, where_clause):
    """Обновляет записи в таблице."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    table_data = load_table_data(table_name)
    updated_count = 0

    # Получаем схему для проверки типов
    columns_schema = {}
    for col_schema in metadata[table_name]:
        if ":" in col_schema:
            col_name, col_type = col_schema.split(":")
            columns_schema[col_name] = col_type

    for row in table_data:
        # Проверяем условие WHERE
        match = True
        for col, val in where_clause.items():
            if str(row.get(col)) != str(val):
                match = False
                break

        if match:
            # Обновляем поля согласно SET
            for col, new_val in set_clause.items():
                if col in columns_schema:
                    try:
                        converted_value = _convert_value(new_val, columns_schema[col])
                        row[col] = converted_value
                    except (ValueError, TypeError) as e:
                        print(f'Ошибка преобразования типа для столбца {col}: {e}')
                        return None
            updated_count += 1

    if updated_count > 0:
        save_table_data(table_name, table_data)
        print(f'Обновлено {updated_count} записей в таблице "{table_name}".')

    return table_data


def delete(table_name, where_clause):
    """Удаляет записи из таблицы."""
    table_data = load_table_data(table_name)

    if not where_clause:
        # Если нет условия, удаляем все
        deleted_count = len(table_data)
        table_data = []
    else:
        # Удаляем по условию
        new_data = []
        for row in table_data:
            match = True
            for col, val in where_clause.items():
                if str(row.get(col)) != str(val):
                    match = False
                    break

            if not match:
                new_data.append(row)

        deleted_count = len(table_data) - len(new_data)
        table_data = new_data

    if deleted_count > 0:
        save_table_data(table_name, table_data)
        print(f'Удалено {deleted_count} записей из таблицы "{table_name}".')

    return table_data


def info_table(metadata, table_name):
    """Выводит информацию о таблице."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    # Загружаем данные таблицы
    table_data = load_table_data(table_name)

    print(f'Таблица: {table_name}')
    print(f'Столбцы: {", ".join(metadata[table_name])}')
    print(f'Количество записей: {len(table_data)}')
