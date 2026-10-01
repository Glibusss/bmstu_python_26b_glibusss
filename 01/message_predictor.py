from __future__ import annotations

import math
from numbers import Real


class SomeModel:  # pylint: disable=too-few-public-methods
    def predict(self, message: str) -> float:
        if not isinstance(message, str):
            raise TypeError("сообщение должно быть строкой")

        example_scores = {
            "чапаев и пустота": 0.9,
            "вулкан": 0.1,
        }
        return example_scores.get(message.casefold(), 0.5)


def _validate_probability(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} должен быть вещественным числом")

    probability = float(value)
    if not math.isfinite(probability):
        raise ValueError(f"{name} должен быть конечным числом")
    if not 0 <= probability <= 1:
        raise ValueError(f"{name} должен находиться в диапазоне от 0 до 1")
    return probability


def predict_message_mood(
    message: str,
    bad_thresholds: float = 0.3,
    good_thresholds: float = 0.8,
) -> str:
    bad_threshold = _validate_probability(bad_thresholds, "нижний порог")
    good_threshold = _validate_probability(
        good_thresholds,
        "верхний порог",
    )
    if bad_threshold >= good_threshold:
        raise ValueError("нижний порог должен быть меньше верхнего порога")

    prediction = _validate_probability(
        SomeModel().predict(message),
        "прогноз модели",
    )
    if prediction < bad_threshold:
        return "неуд"
    if prediction > good_threshold:
        return "отл"
    return "норм"
