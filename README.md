# Тестовое задание Placebo25
REST API для управления структурой компании и правами сотрудников, в зависимости от должности.

Используемый стэк:
1. <a href="https://www.python.org/downloads/release/python-3110/">Python 3.11</a>
2. <a href="https://github.com/tiangolo/fastapi">FastAPI</a>
3. <a href="https://github.com/sqlalchemy/sqlalchemy">SQLAlchemy</a> / <a href="https://github.com/python/cpython/blob/main/Doc/library/sqlite3.rst">SQLite3</a>
4. <a href="https://github.com/pytest-dev/pytest/">Pytest</a>
5. <a href="https://github.com/pydantic/pydantic">Pydantic</a>
6. <a href="https://github.com/encode/uvicorn">Uvicorn</a>
7. <a href="https://github.com/docker">Docker</a>

Порядок запуска:
1. Сделать клон репозитория:
```
git clone https://github.com/porebrikk/placebo25.git
```
3. Перейти в папку **placebo25**;
4. Запустить контейнеры с базой данных и приложением:
```
docker-compose up -d --build
```
6. Для работы с API использовать адрес:
```
http://localhost:8000/
```
7. Запуск тестов производится командой:
```
pytest -svv ./app/
```
