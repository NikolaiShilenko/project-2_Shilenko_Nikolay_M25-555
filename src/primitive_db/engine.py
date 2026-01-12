import prompt


def welcome():
    print("Первая попытка запустить проект!")
    print("***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")
        command = prompt.string("Введите команду: ").strip()

        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            print("Справка:")
            print("  exit - выйти из программы")
            print("  help - показать эту справку")
        else:
            print(f"Неизвестная команда: {command}")