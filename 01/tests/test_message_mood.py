from unittest.mock import Mock, patch

import pytest

from homework import SomeModel, predict_message_mood


@pytest.mark.parametrize(
    ("score", "bad_threshold", "good_threshold", "expected"),
    [
        (0.0, 0.3, 0.8, "неуд"),
        (0.29, 0.3, 0.8, "неуд"),
        (0.3, 0.3, 0.8, "норм"),
        (0.5, 0.3, 0.8, "норм"),
        (0.8, 0.3, 0.8, "норм"),
        (0.81, 0.3, 0.8, "отл"),
        (1.0, 0.3, 0.8, "отл"),
        (0.9, 0.8, 0.99, "норм"),
    ],
)
def test_prediction_categories(
    score,
    bad_threshold,
    good_threshold,
    expected,
):
    model = Mock()
    model.predict.return_value = score

    with patch("homework.SomeModel", return_value=model) as model_class:
        result = predict_message_mood(
            "test message",
            bad_threshold,
            good_threshold,
        )

    assert result == expected
    model_class.assert_called_once_with()
    model.predict.assert_called_once_with("test message")


@pytest.mark.parametrize(
    ("bad_threshold", "good_threshold", "error", "message"),
    [
        (
            "0.3",
            0.8,
            TypeError,
            "нижний порог должен быть вещественным числом",
        ),
        (
            False,
            0.8,
            TypeError,
            "нижний порог должен быть вещественным числом",
        ),
        (
            0.3,
            None,
            TypeError,
            "верхний порог должен быть вещественным числом",
        ),
        (
            -0.1,
            0.8,
            ValueError,
            "нижний порог должен находиться в диапазоне от 0 до 1",
        ),
        (
            0.3,
            1.1,
            ValueError,
            "верхний порог должен находиться в диапазоне от 0 до 1",
        ),
        (
            float("nan"),
            0.8,
            ValueError,
            "нижний порог должен быть конечным числом",
        ),
        (
            0.3,
            float("inf"),
            ValueError,
            "верхний порог должен быть конечным числом",
        ),
        (
            0.8,
            0.8,
            ValueError,
            "нижний порог должен быть меньше верхнего порога",
        ),
        (
            0.9,
            0.8,
            ValueError,
            "нижний порог должен быть меньше верхнего порога",
        ),
    ],
)
def test_invalid_thresholds_raise(
    bad_threshold,
    good_threshold,
    error,
    message,
):
    with pytest.raises(error, match=message):
        predict_message_mood("message", bad_threshold, good_threshold)


@pytest.mark.parametrize(
    ("prediction", "error", "message"),
    [
        (
            "0.5",
            TypeError,
            "прогноз модели должен быть вещественным числом",
        ),
        (
            True,
            TypeError,
            "прогноз модели должен быть вещественным числом",
        ),
        (
            -0.1,
            ValueError,
            "прогноз модели должен находиться в диапазоне от 0 до 1",
        ),
        (
            1.1,
            ValueError,
            "прогноз модели должен находиться в диапазоне от 0 до 1",
        ),
        (
            float("nan"),
            ValueError,
            "прогноз модели должен быть конечным числом",
        ),
        (
            float("-inf"),
            ValueError,
            "прогноз модели должен быть конечным числом",
        ),
    ],
)
def test_invalid_prediction_raises(prediction, error, message):
    with patch("homework.SomeModel.predict", return_value=prediction):
        with pytest.raises(error, match=message):
            predict_message_mood("message")


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Чапаев и пустота", "отл"),
        ("Вулкан", "неуд"),
        ("Неизвестная фраза", "норм"),
    ],
)
def test_example_model_scores(message, expected):
    assert predict_message_mood(message) == expected


@pytest.mark.parametrize("message", [123, None, True])
def test_model_rejects_non_string_message(message):
    with pytest.raises(TypeError, match="сообщение должно быть строкой"):
        SomeModel().predict(message)
