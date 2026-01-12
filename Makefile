install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
ifeq ($(OS),Windows_NT)
	for %%i in (dist\*.whl) do python -m pip install "%%i"
else
	python3 -m pip install dist/*.whl
endif

lint:
	poetry run ruff check .
