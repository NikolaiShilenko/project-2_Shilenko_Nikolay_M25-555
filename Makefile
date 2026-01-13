# Установка зависимостей проекта с помощью Poetry
install:
	poetry install

# Запуск проекта через Poetry (старый интерфейс)
project:
	poetry run project

# Сборка пакета для публикации
build:
	poetry build

# Тестовая публикация пакета в PyPI (без реальной загрузки)
publish:
	poetry publish --dry-run

# Установка собранного пакета в систему.
# Автоматически определяет ОС и использует правильный синтаксис путей.
package-install:
ifeq ($(OS),Windows_NT)
    # Для Windows: находим все .whl файлы в папке dist и устанавливаем их.
    # %%i - переменная цикла, содержит путь к найденному .whl файлу.
    # Кавычки вокруг %%i защищают от пробелов в путях.
	for %%i in (dist\*.whl) do python -m pip install "%%i"
else
    # Для Linux/Mac: используем wildcard для установки любого .whl файла.
	python3 -m pip install dist/*.whl
endif

# Проверка кода линтером Ruff
lint:
	poetry run ruff check .

# Запуск базы данных (основной интерфейс)
database:
	poetry run database