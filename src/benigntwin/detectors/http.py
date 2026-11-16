"""Evaluate a guardrail behind an HTTP endpoint.

One ``POST`` per example with a JSON body. By default the body contains only the
text, for example ``{"text": "..."}``. The response is a JSON object carrying a
label, a score or both; nested values are addressed with dotted paths such as
``result.label``.

The endpoint receives the full input text. Its own logs may keep that text, so
only point this at endpoints that are approved for the data you send.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any

from .._version import __version__
from ..models import Example, ModelError, Prediction
from .base import Detector, DetectorError

__all__ = ["HttpDetector"]

_MISSING = object()
_RETRY_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504})


def _nested(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return _MISSING
        current = current[part]
    return current


class HttpDetector(Detector):
    """POSTs each example to a JSON endpoint."""

    def __init__(
        self,
        endpoint: str,
        *,
        text_field: str = "text",
        label_field: str = "label",
        score_field: str = "score",
        timeout: float = 15.0,
        retries: int = 1,
        token_env: str | None = None,
        headers: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
        send_id: bool = False,
    ) -> None:
        if not endpoint.startswith(("http://", "https://")):
            raise DetectorError("an HTTP detector endpoint must start with http:// or https://")
        if timeout <= 0:
            raise DetectorError("the HTTP timeout must be positive")
        if retries < 0:
            raise DetectorError("HTTP retries cannot be negative")
        self.endpoint = endpoint
        self.text_field = text_field
        self.label_field = label_field
        self.score_field = score_field
        self.timeout = timeout
        self.retries = retries
        self.send_id = send_id
        self._body = dict(body or {})
        self._header_names = sorted(headers or {})
        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"benigntwin/{__version__}",
            **dict(headers or {}),
        }
        self._token_env = token_env
        if token_env:
            token = os.environ.get(token_env)
            if not token:
                raise DetectorError(f"environment variable {token_env} is not set")
            self._headers["Authorization"] = f"Bearer {token}"
        self.name = f"http:{endpoint}"

    def describe(self) -> dict[str, Any]:
        # Header values and the token are left out on purpose.
        return {
            "name": self.name,
            "type": "http",
            "endpoint": self.endpoint,
            "text_field": self.text_field,
            "label_field": self.label_field,
            "score_field": self.score_field,
            "timeout_seconds": self.timeout,
            "retries": self.retries,
            "extra_headers": self._header_names,
            "extra_body_fields": sorted(self._body),
            "authenticated": self._token_env is not None,
        }

    def _request_body(self, example: Example) -> bytes:
        payload: dict[str, Any] = dict(self._body)
        payload[self.text_field] = example.text
        if self.send_id:
            payload["id"] = example.id
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def predict_one(self, example: Example) -> Prediction:
        body = self._request_body(example)
        started = time.perf_counter()
        last_error = "unknown HTTP error"
        for attempt in range(self.retries + 1):
            request = urllib.request.Request(  # noqa: S310 - http(s) only, checked in __init__
                self.endpoint, data=body, headers=self._headers, method="POST"
            )
            try:
                # The constructor only accepts http:// and https:// endpoints.
                with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310
                    payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                exc.close()  # the error object holds the response body
                last_error = f"HTTP {exc.code}"
                if exc.code not in _RETRY_STATUS:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
            except ValueError as exc:
                last_error = f"response is not valid JSON: {exc}"
                break
            else:
                if not isinstance(payload, Mapping):
                    return Prediction(id=example.id, error="response must be a JSON object")
                label = _nested(payload, self.label_field)
                score = _nested(payload, self.score_field)
                value: dict[str, Any] = {}
                if label is not _MISSING:
                    value["label"] = label
                if score is not _MISSING:
                    value["score"] = score
                try:
                    return Prediction.from_value(
                        example.id,
                        value,
                        latency_ms=(time.perf_counter() - started) * 1000.0,
                    )
                except ModelError as exc:
                    return Prediction(
                        id=example.id,
                        error=f"{exc} (looked for {self.label_field!r} and {self.score_field!r})",
                    )
            if attempt < self.retries:
                time.sleep(min(0.25 * (2**attempt), 2.0))
        return Prediction(id=example.id, error=last_error)
