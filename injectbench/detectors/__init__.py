"""Built-in detectors and a small registry."""
from __future__ import annotations

from typing import Dict, Type

from .base import Detector
from .regex_detector import RegexDetector
from .heuristic_detector import HeuristicDetector

_REGISTRY: Dict[str, Type[Detector]] = {
    RegexDetector.name: RegexDetector,
    HeuristicDetector.name: HeuristicDetector,
}


def get_detector(name: str) -> Detector:
    if name not in _REGISTRY:
        raise KeyError(f"unknown detector '{name}'. available: {sorted(_REGISTRY)}")
    return _REGISTRY[name]()


def available_detectors():
    return sorted(_REGISTRY)


def register(cls: Type[Detector]) -> Type[Detector]:
    """Decorator to register a custom detector by its `name`."""
    _REGISTRY[cls.name] = cls
    return cls


__all__ = [
    "Detector",
    "RegexDetector",
    "HeuristicDetector",
    "get_detector",
    "available_detectors",
    "register",
]
