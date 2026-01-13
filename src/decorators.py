import time

import prompt


def handle_db_errors(func):
    """Декоратор для обработки ошибок БД."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(f"Ошибка: Файл данных не найден. {e}")
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец не найден: {e}")
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return None
        except TypeError as e:
            print(f"Ошибка типа данных: {e}")
            return None
        except Exception as e:
            print(f"Произошла неизвестная ошибка: {e}")
            return None

    return wrapper


def confirm_action(action_name):
    """Декоратор для подтверждения опасных операций."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Проверяем, не в kwargs ли передано имя таблицы
            table_name = None
            if len(args) >= 2:
                table_name = args[1]  # Второй аргумент обычно имя таблицы

            if table_name:
                message = (f'Вы уверены, что хотите выполнить "{action_name}" '
                           f'таблицы "{table_name}"? [y/n]: ')
            else:
                message = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '

            answer = prompt.string(message).strip().lower()
            if answer == 'y' or answer == 'yes':
                return func(*args, **kwargs)
            else:
                print("операция отменена.")
                # Возвращаем исходные данные, если операция отменена
                if 'metadata' in kwargs:
                    return kwargs['metadata']
                elif len(args) > 0:
                    return args[0]  # Первый аргумент обычно metadata
                return None

        return wrapper

    return decorator


def log_time(func):
    """декоратор для замера времени выполнения функции."""

    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")
        return result

    return wrapper


def create_cacher():
    """Фабрика для создания функции кэширования."""
    cache = {}

    def cache_result(key, value_func):
        """кэширует результат функции по ключу."""
        if key in cache:
            return cache[key]

        result = value_func()
        cache[key] = result
        return result

    return cache_result
