"""Dataset loading into a common `Example` schema.

Supported sources:
- local ``.jsonl`` (one JSON object per line)
- local ``.parquet``
- a Hugging Face Hub dataset id (needs ``huggingface_hub``; parquet is read with pandas)

Every source is normalized to `Example(text, label, attack_family, language, pair_id)`.
The schema matches the AltaySec / Enes Deniz prompt-injection datasets, so those
load with zero configuration.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Iterable, Dict, Any


@dataclass
class Example:
    text: str
    label: int
    attack_family: str = "unknown"
    language: str = "en"
    pair_id: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


_TEXT_KEYS = ("text", "prompt", "input", "message")
_LABEL_KEYS = ("label", "is_injection", "injection", "target")


def _coerce(rec: Dict[str, Any]) -> Optional[Example]:
    text = next((rec[k] for k in _TEXT_KEYS if k in rec and rec[k] is not None), None)
    if text is None:
        return None
    raw_label = next((rec[k] for k in _LABEL_KEYS if k in rec and rec[k] is not None), None)
    if raw_label is None:
        # fall back to a class string if present
        cls = rec.get("class")
        raw_label = 1 if cls == "injection" else 0
    label = _to_binary(raw_label)
    return Example(
        text=str(text),
        label=label,
        attack_family=str(rec.get("attack_family", rec.get("family", "unknown"))),
        language=str(rec.get("language", rec.get("lang", "en"))),
        pair_id=(str(rec["pair_id"]) if rec.get("pair_id") is not None else None),
        meta={k: v for k, v in rec.items() if k not in _TEXT_KEYS + _LABEL_KEYS},
    )


def _to_binary(v: Any) -> int:
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return 1 if int(v) == 1 else 0
    s = str(v).strip().lower()
    if s in ("1", "injection", "attack", "malicious", "true", "yes", "positive"):
        return 1
    return 0


def load_jsonl(path: str) -> List[Example]:
    out: List[Example] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ex = _coerce(json.loads(line))
            if ex is not None:
                out.append(ex)
    return out


def load_parquet(path: str) -> List[Example]:
    import pandas as pd  # local import keeps pandas optional
    df = pd.read_parquet(path)
    return [ex for ex in (_coerce(r) for r in df.to_dict(orient="records")) if ex is not None]


def load_hf(repo_id: str, split: str = "test") -> List[Example]:
    """Load a split from a Hugging Face Hub dataset by downloading its parquet."""
    from huggingface_hub import hf_hub_download  # optional dependency
    path = hf_hub_download(repo_id=repo_id, filename=f"data/{split}.parquet", repo_type="dataset")
    return load_parquet(path)


def load(source: str, split: str = "test") -> List[Example]:
    """Dispatch on the source string: a file path, or a ``hf:owner/name`` id."""
    if source.startswith("hf:"):
        return load_hf(source[3:], split=split)
    if source.endswith(".jsonl"):
        return load_jsonl(source)
    if source.endswith(".parquet"):
        return load_parquet(source)
    raise ValueError(f"unrecognized dataset source: {source!r}")


def pairs_from(examples: Iterable[Example]):
    """Group examples by ``pair_id`` into (benign, attack) tuples for boundary analysis."""
    by_pair: Dict[str, Dict[int, Example]] = {}
    for ex in examples:
        if ex.pair_id is None:
            continue
        by_pair.setdefault(ex.pair_id, {})[ex.label] = ex
    out = []
    for pid, d in by_pair.items():
        if 0 in d and 1 in d:
            out.append((d[0], d[1]))
    return out
