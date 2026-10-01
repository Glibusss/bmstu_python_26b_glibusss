# Домашнее задание 02

Модуль `event_system.py` содержит систему обработки событий:

- `Event` с уровнем, данными и признаком постоянного хранения;
- абстрактный `EventHandler` с поддержкой виртуальных подклассов;
- обработчики `StreamHandler`, `EmailHandler` и `FileHandler`;
- `EventDispatcher` для регистрации, вызова и удаления обработчиков.

Уровни можно задавать числами из модуля `logging` или строковыми именами.
Каждый обработчик принимает только события своего минимального уровня или
выше. `FileHandler` дополнительно записывает только постоянные события.

## Проверки

Из каталога `02` выполните:

```bash
python -m pip install -r ../requirements-dev.txt
python -m coverage run --rcfile=../.coveragerc -m pytest .
python -m coverage report --rcfile=../.coveragerc
python -m flake8 --config=../.flake8 event_system.py test_event_system.py
python -m pylint --rcfile=../.pylintrc event_system.py test_event_system.py
```

Минимально допустимое покрытие — 90%.
