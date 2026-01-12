import shlex
import prompt
from . import utils
from . import core


def print_help():
    """Выводит справочную информацию."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Основной цикл работы базы данных."""
    print("***База данных***")
    print_help()

    while True:
        # Загружаем актуальные метаданные
        metadata = utils.load_metadata()

        # Получаем команду от пользователя
        user_input = prompt.string(">>>Введите команду: ").strip()

        # Разбиваем на аргументы
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка в синтаксисе команды. Попробуйте снова.")
            continue

        command = args[0] if args else ""

        # Обработка команд
        if command == "exit":
            print("Выход из программы.")
            break

        elif command == "help":
            print_help()

        elif command == "create_table":
            if len(args) < 3:
                print("Ошибка: Недостаточно аргументов. Формат: create_table <имя> <столбец1:тип> ...")
                continue
            table_name = args[1]
            columns = args[2:]
            metadata = core.create_table(metadata, table_name, columns)
            if table_name in metadata:  # Если создание успешно
                utils.save_metadata(metadata)

        elif command == "list_tables":
            core.list_tables(metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print("Ошибка: Неверное количество аргументов. Формат: drop_table <имя>")
                continue
            table_name = args[1]
            old_len = len(metadata)
            metadata = core.drop_table(metadata, table_name)
            if len(metadata) != old_len:  # Если удаление успешно
                utils.save_metadata(metadata)

        else:
            print(f"Функции '{command}' нет. Попробуйте снова.")
