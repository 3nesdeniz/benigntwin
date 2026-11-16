"""Evaluate a Python function: ``python:path/to/file.py:function`` or ``python:module:function``.

The function is called once per example and returns a label, a score or a
mapping with ``label`` and/or ``score``::

    def detect(text: str) -> float:          # receives the text
        return my_model.attack_probability(text)

    def detect(example: dict) -> dict:       # receives {"id": ..., "text": ...}
        return {"label": "attack", "score": 0.93}

If the first parameter is called ``text`` or ``prompt`` the function receives
the text; otherwise it receives a dictionary with ``id`` and ``text``.

Loading a detector imports and runs that file. Only point this at code you trust.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

from ..models import Example, Prediction
from .base import Detector, DetectorError

__all__ = ["PythonDetector"]

_TEXT_PARAMETERS = frozenset({"text", "prompt"})


def _load_module(target: str) -> tuple[ModuleType, str]:
    if ":" not in target:
        raise DetectorError("a Python detector looks like python:path.py:function or python:module:function")
    module_part, function_name = target.rsplit(":", 1)
    path = Path(module_part).expanduser()
    if path.suffix == ".py" or path.exists():
        resolved = path.resolve()
        if not resolved.is_file():
            raise DetectorError(f"Python detector file does not exist: {resolved}")
        module_name = f"injectbench_user_{resolved.stem}_{abs(hash(str(resolved)))}"
        spec = importlib.util.spec_from_file_location(module_name, resolved)
        if spec is None or spec.loader is None:
            raise DetectorError(f"could not import Python detector: {resolved}")
        module = importlib.util.module_from_spec(spec)
        directory = str(resolved.parent)
        sys.path.insert(0, directory)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            raise DetectorError(f"importing {resolved} failed: {type(exc).__name__}: {exc}") from exc
        finally:
            if directory in sys.path:
                sys.path.remove(directory)
        return module, function_name
    try:
        return importlib.import_module(module_part), function_name
    except ImportError as exc:
        raise DetectorError(f"could not import module {module_part!r}: {exc}") from exc


def _wants_text(function: Callable[..., Any]) -> bool:
    try:
        parameters = list(inspect.signature(function).parameters.values())
    except (TypeError, ValueError):
        return False
    return bool(parameters) and parameters[0].name in _TEXT_PARAMETERS


class PythonDetector(Detector):
    """Calls a user-provided function for each example."""

    def __init__(self, target: str) -> None:
        module, function_name = _load_module(target)
        function = getattr(module, function_name, None)
        if not callable(function):
            raise DetectorError(f"function {function_name!r} not found in {target.rsplit(':', 1)[0]}")
        self._function: Callable[[Any], Any] = function
        self._text_argument = _wants_text(function)
        self._target = target
        self.name = f"python:{target}"

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": "python",
            "target": self._target,
            "receives": "text" if self._text_argument else "id and text",
        }

    def predict_one(self, example: Example) -> Prediction:
        argument: Any = example.text if self._text_argument else example.detector_input()
        return Prediction.from_value(example.id, self._function(argument))
