import logging
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from event_system import (
    EmailHandler,
    Event,
    EventDispatcher,
    EventHandler,
    FileHandler,
    StreamHandler,
)


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        (logging.DEBUG, logging.DEBUG),
        ("info", logging.INFO),
        ("WARNING", logging.WARNING),
    ],
)
def test_event_normalizes_level(level, expected):
    event = Event(level, "данные")

    assert event.level == expected


@pytest.mark.parametrize(
    ("arguments", "error", "message"),
    [
        (
            {"level": True, "data": "данные"},
            TypeError,
            "уровень должен быть целым числом или строкой",
        ),
        (
            {"level": 1.5, "data": "данные"},
            TypeError,
            "уровень должен быть целым числом или строкой",
        ),
        (
            {"level": "UNKNOWN", "data": "данные"},
            ValueError,
            "неизвестный уровень события: UNKNOWN",
        ),
        (
            {
                "level": logging.INFO,
                "data": "данные",
                "is_persistent": 1,
            },
            TypeError,
            "признак постоянного хранения должен быть bool",
        ),
    ],
)
def test_invalid_event_arguments(arguments, error, message):
    with pytest.raises(error, match=message):
        Event(**arguments)


def test_event_has_readable_string_representations():
    event = Event("INFO", {"message": "готово"}, True)
    expected = (
        "Event(level=INFO, data={'message': 'готово'}, "
        "is_persistent=True)"
    )

    assert str(event) == expected
    assert repr(event) == expected


def test_event_handler_is_abstract():
    with pytest.raises(TypeError):
        EventHandler()  # pylint: disable=abstract-class-instantiated


class VirtualHandler:
    def __init__(self, handler_type="virtual"):
        self.handler_type = handler_type
        self.events = []

    def handle(self, event):
        self.events.append(event)

    def get_type(self):
        return self.handler_type


class IncompleteHandler:  # pylint: disable=too-few-public-methods
    def handle(self, event):
        return event


class BytesPath:  # pylint: disable=too-few-public-methods
    def __fspath__(self):
        return b"events.log"


def test_event_handler_supports_virtual_subclasses():
    assert issubclass(VirtualHandler, EventHandler)
    assert isinstance(VirtualHandler(), EventHandler)
    assert not issubclass(IncompleteHandler, EventHandler)
    assert not issubclass(VirtualHandler, StreamHandler)


def test_abstract_methods_raise_when_called_directly():
    with pytest.raises(NotImplementedError):
        EventHandler.handle(object(), Event("INFO", "сообщение"))
    with pytest.raises(NotImplementedError):
        EventHandler.get_type(object())


@pytest.mark.parametrize(
    ("handler", "expected"),
    [
        (StreamHandler(), "stream"),
        (EmailHandler("user@example.com"), "email"),
        (FileHandler("events.log"), "file"),
    ],
)
def test_handler_types(handler, expected):
    assert handler.get_type() == expected


@pytest.mark.parametrize(
    ("handler_level", "event_level", "should_print"),
    [
        (logging.INFO, logging.DEBUG, False),
        (logging.INFO, logging.INFO, True),
        (logging.INFO, logging.ERROR, True),
        ("WARNING", "INFO", False),
        ("WARNING", "CRITICAL", True),
    ],
)
def test_stream_handler_filters_by_level(
    handler_level,
    event_level,
    should_print,
    capsys,
):
    event = Event(event_level, "сообщение")
    StreamHandler(handler_level).handle(event)

    output = capsys.readouterr().out
    assert bool(output) is should_print
    if should_print:
        assert output == f"{event}\n"


@pytest.mark.parametrize(
    ("handler_level", "event_level", "should_send"),
    [
        (logging.WARNING, logging.INFO, False),
        (logging.WARNING, logging.WARNING, True),
        (logging.WARNING, logging.CRITICAL, True),
    ],
)
def test_email_handler_filters_by_level(
    handler_level,
    event_level,
    should_send,
):
    event = Event(event_level, "сообщение")
    handler = EmailHandler("user@example.com", handler_level)

    with patch.object(handler, "send_email") as send_email:
        handler.handle(event)

    if should_send:
        level_name = logging.getLevelName(event.level)
        send_email.assert_called_once_with(
            "user@example.com",
            f"Событие уровня {level_name}",
            str(event),
        )
    else:
        send_email.assert_not_called()


def test_send_email_prints_all_fields(capsys):
    handler = EmailHandler("user@example.com")

    handler.send_email("user@example.com", "Тема", "Тело")

    assert capsys.readouterr().out == (
        "Получатель: user@example.com\n"
        "Тема: Тема\n"
        "Тело\n"
    )


@pytest.mark.parametrize(
    (
        "handler_level",
        "event_level",
        "is_persistent",
        "should_write",
    ),
    [
        (logging.INFO, logging.DEBUG, True, False),
        (logging.INFO, logging.INFO, False, False),
        (logging.INFO, logging.INFO, True, True),
        (logging.INFO, logging.CRITICAL, True, True),
    ],
)
def test_file_handler_filters_by_level_and_persistence(
    handler_level,
    event_level,
    is_persistent,
    should_write,
):
    event = Event(event_level, "сообщение", is_persistent)
    handler = FileHandler("events.log", handler_level)

    with patch("builtins.open", mock_open()) as opened_file:
        handler.handle(event)

    if should_write:
        opened_file.assert_called_once_with(
            "events.log",
            "a",
            encoding="utf-8",
        )
        opened_file().write.assert_called_once_with(f"{event}\n")
    else:
        opened_file.assert_not_called()


@pytest.mark.parametrize(
    ("handler_factory", "message"),
    [
        (
            lambda: StreamHandler(True),
            "уровень должен быть целым числом или строкой",
        ),
        (
            lambda: StreamHandler("UNKNOWN"),
            "неизвестный уровень события: UNKNOWN",
        ),
        (
            lambda: EmailHandler(123),
            "получатель должен быть строкой",
        ),
        (
            lambda: EmailHandler("   "),
            "получатель не должен быть пустым",
        ),
        (
            lambda: FileHandler(123),
            "имя файла должно быть строкой или путем",
        ),
        (
            lambda: FileHandler(""),
            "имя файла не должно быть пустым",
        ),
        (
            lambda: FileHandler(BytesPath()),
            "имя файла должно быть строкой или путем",
        ),
    ],
)
def test_invalid_handler_configuration(handler_factory, message):
    with pytest.raises((TypeError, ValueError), match=message):
        handler_factory()


def test_file_handler_accepts_path_like_filename():
    handler = FileHandler(Path("events.log"))

    assert handler.filename == "events.log"


@pytest.mark.parametrize(
    "handler",
    [
        StreamHandler(),
        EmailHandler("user@example.com"),
        FileHandler("events.log"),
    ],
)
def test_handlers_reject_non_event(handler):
    with pytest.raises(
        TypeError,
        match="обработчик принимает только объекты Event",
    ):
        handler.handle("не событие")


def test_dispatcher_calls_all_registered_handlers():
    first_handler = VirtualHandler("first")
    second_handler = VirtualHandler("second")
    dispatcher = EventDispatcher()
    dispatcher.register_handler(first_handler)
    dispatcher.register_handler(second_handler)
    event = Event("INFO", "сообщение")

    dispatcher.dispatch(event)

    assert first_handler.events == [event]
    assert second_handler.events == [event]


def test_dispatcher_removes_all_handlers_of_selected_type():
    first_email = VirtualHandler("email")
    second_email = VirtualHandler("email")
    stream = VirtualHandler("stream")
    dispatcher = EventDispatcher()
    dispatcher.register_handler(first_email)
    dispatcher.register_handler(second_email)
    dispatcher.register_handler(stream)
    event = Event("INFO", "сообщение")

    dispatcher.remove_handler("email")
    dispatcher.dispatch(event)

    assert not first_email.events
    assert not second_email.events
    assert stream.events == [event]


def test_dispatcher_keeps_handlers_for_unknown_type():
    handler = VirtualHandler("stream")
    dispatcher = EventDispatcher()
    dispatcher.register_handler(handler)
    event = Event("INFO", "сообщение")

    dispatcher.remove_handler("unknown")
    dispatcher.dispatch(event)

    assert handler.events == [event]


@pytest.mark.parametrize(
    ("operation", "argument", "message"),
    [
        (
            "register_handler",
            object(),
            "обработчик должен соответствовать EventHandler",
        ),
        (
            "dispatch",
            "не событие",
            "диспетчер принимает только объекты Event",
        ),
        (
            "remove_handler",
            123,
            "тип обработчика должен быть строкой",
        ),
    ],
)
def test_dispatcher_rejects_invalid_arguments(operation, argument, message):
    dispatcher = EventDispatcher()

    with pytest.raises(TypeError, match=message):
        getattr(dispatcher, operation)(argument)


def test_dispatch_uses_snapshot_of_handlers():
    dispatcher = EventDispatcher()
    late_handler = VirtualHandler("late")

    class RegisteringHandler:
        @staticmethod
        def get_type():
            return "registering"

        @staticmethod
        def handle(_event):
            dispatcher.register_handler(late_handler)

    dispatcher.register_handler(RegisteringHandler())

    dispatcher.dispatch(Event("INFO", "первое"))

    assert not late_handler.events

    second_event = Event("INFO", "второе")
    dispatcher.dispatch(second_event)

    assert late_handler.events == [second_event]
