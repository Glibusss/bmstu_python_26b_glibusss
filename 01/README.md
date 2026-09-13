# Домашнее задание 01

Решение содержит две части:

- `predict_message_mood` создаёт `SomeModel`, получает оценку сообщения и
  возвращает `"неуд"`, `"норм"` или `"отл"`;
- `filter_file` лениво фильтрует строки пути или открытого текстового файла по
  полным словам без учёта регистра, причём стоп-слова имеют приоритет.

## Контракт ошибок

Пороги и прогноз должны быть вещественными конечными числами в диапазоне
`[0, 1]`; `bool` числом не считается. Неверный тип вызывает `TypeError`, а
неверное значение — `ValueError`. Нижний порог должен быть строго меньше
верхнего. Оценка, равная одному из порогов, относится к категории `"норм"`.

## Проверки

Зависимости и настройки `pytest`, `coverage`, `flake8` и `pylint` общие для
всего репозитория и находятся в родительской папке. Из папки `01` выполните:

```bash
python -m pip install -r ../requirements-dev.txt
python -m coverage run --rcfile=../.coveragerc -m pytest tests
python -m coverage report --rcfile=../.coveragerc
python -m flake8 --config=../.flake8 homework.py tests
python -m pylint --rcfile=../.pylintrc homework.py tests
```

Минимально допустимое покрытие - 90%. Те же команды запускаются вручную через
GitHub Actions workflow `.github/workflows/homework-01.yml` в корне репозитория.
