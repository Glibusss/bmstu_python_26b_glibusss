from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass


def _normalize_level(level: int | str) -> int:
    if isinstance(level, bool) or not isinstance(level, (int, str)):
        raise TypeError("уровень должен быть целым числом или строкой")

    if isinstance(level, int):
        return level

    normalized_level = logging.getLevelNamesMapping().get(level.upper())
    if normalized_level is None:
        raise ValueError(f"неизвестный уровень события: {level}")
    return normalized_level


@dataclass(slots=True)
class Event:
    level: int | str
    data: object
    is_persistent: bool = False

    def __post_init__(self) -> None:
        self.level = _normalize_level(self.level)
        if not isinstance(self.is_persistent, bool):
            raise TypeError("признак постоянного хранения должен быть bool")

    def __str__(self) -> str:
        level_name = logging.getLevelName(self.level)
        return (
            f"Event(level={level_name}, data={self.data!r}, "
            f"is_persistent={self.is_persistent})"
        )

    def __repr__(self) -> str:
        return str(self)


class EventHandler(ABC):
    def __init__(self, level: int | str = logging.NOTSET) -> None:
        self.level = _normalize_level(level)

    @abstractmethod
    def handle(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_type(self) -> str:
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is EventHandler:
            required_methods = ("handle", "get_type")
            supports_protocol = all(
                any(
                    callable(base.__dict__.get(method_name))
                    for base in subclass.__mro__
                )
                for method_name in required_methods
            )
            if supports_protocol:
                return True
        return NotImplemented

    def _can_handle(self, event: Event) -> bool:
        if not isinstance(event, Event):
            raise TypeError("обработчик принимает только объекты Event")
        return event.level >= self.level


class StreamHandler(EventHandler):
    def handle(self, event: Event) -> None:
        if self._can_handle(event):
            print(event)

    def get_type(self) -> str:
        return "stream"


class EmailHandler(EventHandler):
    def __init__(
        self,
        recipient: str,
        level: int | str = logging.NOTSET,
    ) -> None:
        super().__init__(level)
        if not isinstance(recipient, str):
            raise TypeError("получатель должен быть строкой")
        if not recipient.strip():
            raise ValueError("получатель не должен быть пустым")
        self.recipient = recipient

    def handle(self, event: Event) -> None:
        if not self._can_handle(event):
            return

        level_name = logging.getLevelName(event.level)
        self.send_email(
            self.recipient,
            f"Событие уровня {level_name}",
            str(event),
        )

    def get_type(self) -> str:
        return "email"

    def send_email(self, recipient: str, subject: str, body: str) -> None:
        print(f"Получатель: {recipient}")
        print(f"Тема: {subject}")
        print(body)


class FileHandler(EventHandler):
    def __init__(
        self,
        filename: str | os.PathLike[str],
        level: int | str = logging.NOTSET,
    ) -> None:
        super().__init__(level)
        if not isinstance(filename, (str, os.PathLike)):
            raise TypeError("имя файла должно быть строкой или путем")

        normalized_filename = os.fspath(filename)
        if not isinstance(normalized_filename, str):
            raise TypeError("имя файла должно быть строкой или путем")
        if not normalized_filename:
            raise ValueError("имя файла не должно быть пустым")
        self.filename = normalized_filename

    def handle(self, event: Event) -> None:
        if not self._can_handle(event) or not event.is_persistent:
            return

        with open(self.filename, "a", encoding="utf-8") as event_file:
            event_file.write(f"{event}\n")

    def get_type(self) -> str:
        return "file"


class EventDispatcher:
    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def register_handler(self, handler: EventHandler) -> None:
        if not isinstance(handler, EventHandler):
            raise TypeError("обработчик должен соответствовать EventHandler")
        self._handlers.append(handler)

    def dispatch(self, event: Event) -> None:
        if not isinstance(event, Event):
            raise TypeError("диспетчер принимает только объекты Event")
        for handler in tuple(self._handlers):
            handler.handle(event)

    def remove_handler(self, handler_type: str) -> None:
        if not isinstance(handler_type, str):
            raise TypeError("тип обработчика должен быть строкой")
        self._handlers = [
            handler
            for handler in self._handlers
            if handler.get_type() != handler_type
        ]
