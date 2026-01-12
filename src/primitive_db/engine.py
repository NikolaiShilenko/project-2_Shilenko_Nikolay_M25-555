import shlex

import prompt
from prettytable import PrettyTable

from ..decorators import create_cacher
from . import core, utils
from .parser import parse_set, parse_where


def print_help():
    """Выводит справочную информацию."""
    print("\n***Операции с данными***")
    print("Функции управления таблицами:")
    print("<command> create_table <имя_таблицы> "
          "<столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nФункции работы с данными:")
    print("<command> insert into <имя_таблицы> values "
          "(<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> "
          "where <столбец> = <значение> - прочитать записи по условию")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
          "where <столбец_условия> = <значение_условия> - обновить запись")
    print("<command> delete from <имя_таблицы> "
          "where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print("***Операции с данными***")
    print_help()

    # Создаем кэш для select запросов
    cacher = create_cacher()

    while True:
        # загрузить актуальные метаданные
        metadata = utils.load_metadata()

        # Получаем команду от пользователя
        user_input = prompt.string(">>>Введите команду: ").strip()

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка в синтаксисе команды. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0].lower()

        # Обработка команд
        if command == "exit":
            print("Выход из программы.")
            break

        elif command == "help":
            print_help()

        elif command == "create_table":
            if len(args) < 3:
                print("Ошибка: Недостаточно аргументов. "
                      "Формат: create_table <имя> <столбец1:тип> <столбец2:тип> ...")
                continue
            table_name = args[1]
            columns = args[2:]
            new_metadata = core.create_table(metadata, table_name, columns)
            if new_metadata is not None and table_name in new_metadata:
                metadata = new_metadata
                utils.save_metadata(metadata)

        elif command == "list_tables":
            core.list_tables(metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print("Ошибка: Неверное количество аргументов. "
                      "Формат: drop_table <имя>")
                continue
            table_name = args[1]
            new_metadata = core.drop_table(metadata, table_name)
            if new_metadata is not None and table_name not in new_metadata:
                metadata = new_metadata
                utils.save_metadata(metadata)

        elif command == "info":
            if len(args) != 2:
                print("Ошибка: Неверное количество аргументов. "
                      "Формат: info <имя_таблицы>")
                continue
            table_name = args[1]
            core.info_table(metadata, table_name)

        elif command == "insert":
            # проверка базового формат: insert into <table> values (...)
            if (len(args) < 4 or args[1].lower() != "into"
                    or args[3].lower() != "values"):
                print("Ошибка: Неверный формат. "
                      "Должно быть: insert into "
                      "<таблица> values (...)")
                continue

            table_name = args[2]

            # собираем все значения после "values"
            values_start = 4
            values_str = " ".join(args[values_start:])

            # Убираем скобки если есть
            if values_str.startswith("(") and values_str.endswith(")"):
                values_str = values_str[1:-1]

            # разбитьзначения по запятым
            # исползуем shlex для корректной обработки строк в кавычках
            try:
                values = shlex.split(values_str.replace(',', ' '))
            except ValueError:
                # Если ошибка, пробуем простой способ
                values = [v.strip() for v in values_str.split(",") if v.strip()]

            # вызов insert
            core.insert(metadata, table_name, values)

        elif command == "select":
            # Формат: select from <table> [where ...]
            if len(args) < 3 or args[1].lower() != "from":
                print("Ошибка: Неверный формат. "
                      "Должно быть: select from <таблица> [where ...]")
                continue

            table_name = args[2]

            if len(args) > 4 and args[3].lower() == "where":
                # Есть условие WHERE
                where_str = " ".join(args[4:])
                where_clause = parse_where(where_str)
                if not where_clause:
                    print("Ошибка: Некорректное условие WHERE")
                    continue

                data = core.select(table_name, where_clause, cacher)
            else:
                # без WHERE
                data = core.select(table_name, None, cacher)

            # вывод результата через PrettyTable
            if data:
                # получаем заголовки из первой записи
                headers = list(data[0].keys())
                table = PrettyTable()
                table.field_names = headers

                for row in data:
                    table.add_row([row[h] for h in headers])

                print(table)
            else:
                print("Нет данных для отображения.")

        elif command == "update":
            # Формат: update <table> set ... where ...
            if len(args) < 6:
                print("Ошибка: Неверный формат. "
                      "Должно быть: update <таблица> set ... where ...")
                continue

            table_name = args[1]

            # найти индексы set и where
            set_idx = -1
            where_idx = -1

            for i, arg in enumerate(args):
                if arg.lower() == "set":
                    set_idx = i
                elif arg.lower() == "where":
                    where_idx = i

            if set_idx == -1 or where_idx == -1:
                print("Ошибка: Отсутствуют SET или WHERE в команде UPDATE")
                continue

            # парсинг SET
            set_str = " ".join(args[set_idx + 1:where_idx])
            set_clause = parse_set(set_str)
            if not set_clause:
                print("Ошибка: Некорректное условие SET")
                continue

            # парсинг WHERE
            where_str = " ".join(args[where_idx + 1:])
            where_clause = parse_where(where_str)
            if not where_clause:
                print("Ошибка: Некорректное условие WHERE")
                continue

            # вызываем update
            core.update(metadata, table_name, set_clause, where_clause)

        elif command == "delete":
            if len(args) < 3 or args[1].lower() != "from":
                print("Ошибка: Неверный формат. "
                      "Должно быть: delete from <таблица> [where ...]")
                continue

            table_name = args[2]

            if len(args) > 4 and args[3].lower() == "where":
                where_str = " ".join(args[4:])
                where_clause = parse_where(where_str)
                if not where_clause:
                    print("Ошибка: Некорректное условие WHERE")
                    continue

                core.delete(table_name, where_clause)
            else:
                # Без условия WHERE - удаляем все
                confirm = prompt.string("Вы уверены, что хотите удалить "
                                        "ВСЕ записи из таблицы? (yes/no): ")
                if confirm.lower() == "yes":
                    core.delete(table_name, None)
                else:
                    print("Операция отменена.")

        else:
            print(f"Функции '{command}' нет. Попробуйте снова.")
