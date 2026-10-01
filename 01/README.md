# Домашнее задание 01

Решение содержит две части:

- `message_predictor.py` содержит `SomeModel` и `predict_message_mood`;
- `file_filter.py` содержит ленивый генератор `filter_file`.

Тестовые модули `test_message_predictor.py` и `test_file_filter.py` находятся
в корне каталога домашнего задания вместе с модулями решения.

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
python -m coverage run --rcfile=../.coveragerc -m pytest .
python -m coverage report --rcfile=../.coveragerc
python -m flake8 --config=../.flake8 message_predictor.py file_filter.py \
    test_message_predictor.py test_file_filter.py
python -m pylint --rcfile=../.pylintrc message_predictor.py file_filter.py \
    test_message_predictor.py test_file_filter.py
```

Минимально допустимое покрытие - 90%. Те же команды запускаются вручную через
GitHub Actions workflow `.github/workflows/homework-01.yml` в корне репозитория.
