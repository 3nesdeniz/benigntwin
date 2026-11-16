"""Export a dataset as a Promptfoo test suite for a detector endpoint.

Writes ``promptfooconfig.yaml``, ``tests.json``, ``provider.py`` and ``RUN.md``.
The provider posts only the input text to the endpoint, so the system under
test never receives labels or attack families.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from .models import Example

__all__ = ["export_promptfoo"]

_PROVIDER_SOURCE = '''"""Promptfoo provider for a binary prompt-injection detector endpoint.

Environment:
    BENIGNTWIN_ENDPOINT     URL that accepts a JSON POST (required)
    BENIGNTWIN_TEXT_FIELD   request field for the input text (default: text)
    BENIGNTWIN_LABEL_FIELD  dotted path of the label in the response (default: label)
    BENIGNTWIN_TOKEN        bearer token (optional)
"""

import json
import os
import urllib.request

_ATTACK = {"1", "attack", "blocked", "injection", "jailbreak", "malicious", "prompt_injection", "unsafe", "true", "yes"}
_BENIGN = {"0", "allowed", "benign", "legitimate", "safe", "false", "no"}


def _normalize(value):
    if isinstance(value, bool):
        return "attack" if value else "benign"
    text = str(value).strip().casefold().replace("-", "_").replace(" ", "_")
    if text in _ATTACK:
        return "attack"
    if text in _BENIGN:
        return "benign"
    raise ValueError(f"unsupported detector label: {value!r}")


def _nested(payload, path):
    current = payload
    for part in path.split("."):
        current = current[part]
    return current


def call_api(prompt, options, context):
    endpoint = os.environ["BENIGNTWIN_ENDPOINT"]
    if not endpoint.startswith(("http://", "https://")):
        raise ValueError("BENIGNTWIN_ENDPOINT must be an http(s) URL")
    body = {os.getenv("BENIGNTWIN_TEXT_FIELD", "text"): prompt}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    token = os.getenv("BENIGNTWIN_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    return {"output": _normalize(_nested(result, os.getenv("BENIGNTWIN_LABEL_FIELD", "label")))}
'''


def export_promptfoo(
    examples: Sequence[Example],
    output_dir: str | Path,
    *,
    dataset_source: str,
    split: str,
) -> dict[str, Path]:
    """Write a runnable Promptfoo suite into ``output_dir`` and return the file paths."""

    target = Path(output_dir).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "config": target / "promptfooconfig.yaml",
        "tests": target / "tests.json",
        "provider": target / "provider.py",
        "instructions": target / "RUN.md",
    }
    tests = [
        {
            "description": example.id,
            "vars": {"text": example.text},
            "metadata": {
                "id": example.id,
                "language": example.language,
                "attack_family": example.attack_family,
                "pair_id": example.pair_id,
            },
            "assert": [
                {
                    "type": "equals",
                    "value": "attack" if example.label == 1 else "benign",
                    "metric": "prompt-injection-classification",
                }
            ],
        }
        for example in examples
    ]
    paths["tests"].write_text(json.dumps(tests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["config"].write_text(
        "\n".join(
            [
                "# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json",
                f"description: {json.dumps(f'BenignTwin export: {dataset_source} ({split})')}",
                "prompts:",
                '  - "{{text}}"',
                "providers:",
                '  - id: "file://provider.py"',
                '    label: "Prompt-injection detector"',
                'tests: "file://tests.json"',
                'outputPath: "results.json"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["provider"].write_text(_PROVIDER_SOURCE, encoding="utf-8")
    paths["instructions"].write_text(
        "\n".join(
            [
                "# Run this export with Promptfoo",
                "",
                f"- Dataset: `{dataset_source}`",
                f"- Split: `{split}`",
                f"- Examples: {len(examples)}",
                "",
                "```bash",
                "export BENIGNTWIN_ENDPOINT=https://your-detector.example/v1/classify",
                "# optional: export BENIGNTWIN_TOKEN=...",
                "npx promptfoo@latest eval -c promptfooconfig.yaml",
                "npx promptfoo@latest view",
                "```",
                "",
                "The endpoint receives only the input text. It must answer with a JSON label at",
                "`label`; set `BENIGNTWIN_LABEL_FIELD` for a nested path such as `result.label`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return paths
