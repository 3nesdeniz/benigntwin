"""Dataset loading and structural validation.

Sources:

* a local ``.jsonl`` / ``.ndjson`` / ``.json`` / ``.parquet`` file;
* a local directory with ``data/<split>.jsonl`` (or ``.parquet``) files;
* a dataset on the Hugging Face Hub: ``hf:owner/name`` or ``hf:owner/name@revision``.

Loading uses only the standard library. Reading ``.parquet`` needs ``pyarrow``
(``pip install "benigntwin[parquet]"``).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from statistics import median
from typing import Any

from ._version import __version__
from .models import (
    BenignTwinError,
    Example,
    ModelError,
    normalize_family,
    normalize_label,
    normalize_language,
)

__all__ = [
    "SPLITS",
    "Dataset",
    "DatasetError",
    "DatasetInfo",
    "FieldMap",
    "SourceFile",
    "ValidationResult",
    "cache_dir",
    "load_dataset",
    "validate_examples",
]

SPLITS: tuple[str, ...] = ("train", "validation", "test")
_HUB_PREFIXES = ("hf://", "hf:")
_JSONL_SUFFIXES = (".jsonl", ".ndjson")


class DatasetError(BenignTwinError):
    """A dataset cannot be found, read or parsed."""


@dataclass(frozen=True, slots=True)
class FieldMap:
    """Which source columns feed which :class:`~benigntwin.models.Example` field.

    Each entry lists accepted column names in order of preference. An empty
    ``id`` tuple means "always generate ids from row order".
    """

    text: tuple[str, ...] = ("text", "prompt", "input", "message")
    label: tuple[str, ...] = ("label", "is_injection", "is_attack", "class")
    id: tuple[str, ...] = ("id", "example_id", "uid")
    language: tuple[str, ...] = ("language", "lang")
    pair_id: tuple[str, ...] = ("pair_id",)
    attack_family: tuple[str, ...] = ("attack_family", "family")
    pair_family: tuple[str, ...] = ("pair_family",)
    split: tuple[str, ...] = ("split",)
    default_language: str | None = None
    default_label: int | None = None

    @classmethod
    def from_options(
        cls,
        *,
        text_field: str | None = None,
        label_field: str | None = None,
        id_field: str | None = None,
        language_field: str | None = None,
        pair_field: str | None = None,
        family_field: str | None = None,
        default_language: str | None = None,
        default_label: Any = None,
    ) -> FieldMap:
        """Build a map from command-line style overrides."""

        base = cls()
        return cls(
            text=(text_field,) if text_field else base.text,
            label=(label_field,) if label_field else base.label,
            id=() if id_field == "auto" else ((id_field,) if id_field else base.id),
            language=(language_field,) if language_field else base.language,
            pair_id=(pair_field,) if pair_field else base.pair_id,
            attack_family=(family_field,) if family_field else base.attack_family,
            pair_family=base.pair_family,
            split=base.split,
            default_language=default_language,
            default_label=None if default_label is None else normalize_label(default_label),
        )


@dataclass(frozen=True, slots=True)
class SourceFile:
    """One file that contributed rows, with its content hash."""

    path: str
    sha256: str
    rows: int


@dataclass(frozen=True, slots=True)
class DatasetInfo:
    """Where the examples came from, precisely enough to load them again."""

    source: str
    kind: str
    split: str
    revision: str | None = None
    resolved_revision: str | None = None
    files: tuple[SourceFile, ...] = ()
    generated_ids: int = 0
    filters: tuple[tuple[str, str], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "kind": self.kind,
            "split": self.split,
            "revision": self.revision,
            "resolved_revision": self.resolved_revision,
            "filters": dict(self.filters),
            "files": [{"path": f.path, "sha256": f.sha256, "rows": f.rows} for f in self.files],
            "generated_ids": self.generated_ids,
        }


@dataclass(frozen=True, slots=True)
class Dataset:
    """Loaded examples plus provenance."""

    examples: tuple[Example, ...]
    info: DatasetInfo

    def __len__(self) -> int:
        return len(self.examples)

    def __iter__(self) -> Iterator[Example]:
        return iter(self.examples)


# ----------------------------------------------------------------------------
# Row conversion
# ----------------------------------------------------------------------------


def _first(row: Mapping[str, Any], names: Sequence[str]) -> tuple[str | None, Any]:
    for name in names:
        if row.get(name) is not None:
            return name, row[name]
    return None, None


def _clean_optional(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def example_from_row(
    row: Mapping[str, Any],
    *,
    field_map: FieldMap,
    fallback_id: str,
    fallback_split: str | None = None,
) -> tuple[Example, bool]:
    """Convert one source row. Returns the example and whether its id was generated."""

    text_name, text = _first(row, field_map.text)
    if not isinstance(text, str) or not text.strip():
        raise ModelError(f"missing or empty text (looked for: {', '.join(field_map.text)})")

    _, raw_label = _first(row, field_map.label)
    if raw_label is None:
        if field_map.default_label is None:
            raise ModelError(f"missing label (looked for: {', '.join(field_map.label)})")
        label = field_map.default_label
    else:
        label = normalize_label(raw_label)

    _, raw_id = _first(row, field_map.id)
    example_id = _clean_optional(raw_id)
    generated = example_id is None

    _, raw_language = _first(row, field_map.language)
    _, raw_family = _first(row, field_map.attack_family)
    _, raw_pair_family = _first(row, field_map.pair_family)
    _, raw_pair = _first(row, field_map.pair_id)
    _, raw_split = _first(row, field_map.split)

    fields = {
        key: value
        for key, value in row.items()
        if key != text_name and (value is None or isinstance(value, (str, int, float, bool)))
    }
    example = Example(
        id=example_id or fallback_id,
        text=text,
        label=label,
        language=normalize_language(raw_language if raw_language is not None else field_map.default_language),
        attack_family=normalize_family(raw_family, label=label),
        pair_family=normalize_family(raw_pair_family, label=0),
        pair_id=_clean_optional(raw_pair),
        split=_clean_optional(raw_split) or fallback_split,
        fields=fields,
    )
    return example, generated


# ----------------------------------------------------------------------------
# File readers
# ----------------------------------------------------------------------------


def _rows_from_jsonl(content: str, origin: str) -> list[tuple[int, Mapping[str, Any]]]:
    rows: list[tuple[int, Mapping[str, Any]]] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DatasetError(f"{origin}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise DatasetError(f"{origin}:{line_number}: each line must be a JSON object")
        rows.append((line_number, payload))
    return rows


def _rows_from_json(content: str, origin: str) -> list[tuple[int, Mapping[str, Any]]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise DatasetError(f"{origin}: invalid JSON: {exc.msg}") from exc
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise DatasetError(f"{origin}: a .json dataset must be a list of objects")
    return list(enumerate(payload, start=1))


def _rows_from_parquet(path: Path) -> list[tuple[int, Mapping[str, Any]]]:
    try:
        import pyarrow.parquet as parquet
    except ImportError as exc:
        raise DatasetError(
            f'{path.name} is a .parquet file; reading it needs pyarrow: pip install "benigntwin[parquet]"'
        ) from exc
    try:
        table = parquet.read_table(path)
    except Exception as exc:  # pyarrow raises its own error types
        raise DatasetError(f"could not read {path}: {exc}") from exc
    return list(enumerate(table.to_pylist(), start=1))


def _read_rows(path: Path, origin: str) -> tuple[list[tuple[int, Mapping[str, Any]]], str]:
    """Return ``(rows, sha256)`` for one data file."""

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise DatasetError(f"could not read {origin}: {exc}") from exc
    digest = hashlib.sha256(raw).hexdigest()
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return _rows_from_parquet(path), digest
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DatasetError(f"{origin}: not valid UTF-8") from exc
    if suffix in _JSONL_SUFFIXES:
        return _rows_from_jsonl(content, origin), digest
    if suffix == ".json":
        return _rows_from_json(content, origin), digest
    raise DatasetError(f"{origin}: unsupported file type {suffix or '(none)'}; use .jsonl, .json or .parquet")


class _Collector:
    """Turns rows from several files into examples with stable generated ids."""

    def __init__(self, field_map: FieldMap, where: Mapping[str, str] | None = None) -> None:
        self.field_map = field_map
        self.where = dict(where or {})
        self.examples: list[Example] = []
        self.files: list[SourceFile] = []
        self.generated_ids = 0

    @property
    def filters(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self.where.items()))

    def add_file(self, path: Path, origin: str, *, fallback_split: str | None) -> None:
        rows, digest = _read_rows(path, origin)
        for line_number, row in rows:
            if any(str(row.get(key)) != value for key, value in self.where.items()):
                continue
            fallback_id = f"row-{len(self.examples) + 1:06d}"
            try:
                example, generated = example_from_row(
                    row,
                    field_map=self.field_map,
                    fallback_id=fallback_id,
                    fallback_split=fallback_split,
                )
            except ModelError as exc:
                raise DatasetError(f"{origin}:{line_number}: {exc}") from exc
            self.generated_ids += int(generated)
            self.examples.append(example)
        self.files.append(SourceFile(path=origin, sha256=digest, rows=len(rows)))


def _filter_hint(collector: _Collector) -> str:
    if not collector.where:
        return ""
    conditions = ", ".join(f"{key}={value}" for key, value in collector.filters)
    return f" matching {conditions}"


# ----------------------------------------------------------------------------
# Hugging Face Hub
# ----------------------------------------------------------------------------


def cache_dir() -> Path:
    """Directory for downloaded datasets (``BENIGNTWIN_CACHE_DIR`` overrides it)."""

    override = os.environ.get("BENIGNTWIN_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "benigntwin"


def _hub_endpoint() -> str:
    return os.environ.get("HF_ENDPOINT", "https://huggingface.co").rstrip("/")


def _http_get(url: str, *, timeout: float = 60.0) -> bytes:
    headers = {"User-Agent": f"benigntwin/{__version__}"}
    token = os.environ.get("HF_TOKEN")
    if token and url.startswith(_hub_endpoint() + "/"):
        headers["Authorization"] = f"Bearer {token}"
    if not url.startswith(("https://", "http://")):
        raise DatasetError(f"refusing to fetch a non-HTTP URL: {url}")
    # Only http(s) URLs reach this point (checked above).
    request = urllib.request.Request(url, headers=headers)  # noqa: S310
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return bytes(response.read())


def _parse_hub_source(source: str, revision: str | None) -> tuple[str, str | None]:
    identifier = source
    for prefix in _HUB_PREFIXES:
        if identifier.startswith(prefix):
            identifier = identifier[len(prefix) :]
            break
    inline_revision: str | None = None
    if "@" in identifier:
        identifier, inline_revision = identifier.rsplit("@", 1)
    if not re.fullmatch(r"[A-Za-z0-9][\w.-]*/[A-Za-z0-9][\w.-]*", identifier):
        raise DatasetError("Hugging Face sources look like hf:owner/name or hf:owner/name@revision")
    if inline_revision and revision and inline_revision != revision:
        raise DatasetError("two different revisions given: one in the source and one as an option")
    return identifier, inline_revision or revision


def _resolve_hub_revision(repo_id: str, revision: str) -> str | None:
    """Ask the Hub which commit a branch or tag points at. ``None`` if unknown."""

    url = (
        f"{_hub_endpoint()}/api/datasets/{urllib.parse.quote(repo_id, safe='/')}"
        f"/revision/{urllib.parse.quote(revision, safe='')}"
    )
    try:
        payload = json.loads(_http_get(url, timeout=30.0))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None
    sha = payload.get("sha") if isinstance(payload, dict) else None
    return sha if isinstance(sha, str) and sha else None


def _safe_repo_path(path: str) -> PurePosixPath:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise DatasetError(f"not a valid path inside a dataset repository: {path!r}")
    return candidate


def _fetch_hub_file(
    repo_id: str,
    revision: str,
    path: str,
    *,
    root: Path,
    refresh: bool,
) -> Path | None:
    """Download one file of a Hub dataset into the cache. ``None`` if it does not exist."""

    relative = _safe_repo_path(path)
    destination = root.joinpath(*relative.parts)
    if destination.is_file() and not refresh:
        return destination
    url = (
        f"{_hub_endpoint()}/datasets/{urllib.parse.quote(repo_id, safe='/')}/resolve/"
        f"{urllib.parse.quote(revision, safe='')}/{urllib.parse.quote(str(relative), safe='/')}"
    )
    try:
        content = _http_get(url)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise DatasetError(
                f"{repo_id}: access denied (HTTP {exc.code}); set HF_TOKEN for gated or private datasets"
            ) from exc
        if exc.code == 404:
            return None
        raise DatasetError(f"could not download {path} from {repo_id}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        if destination.is_file():
            return destination
        raise DatasetError(f"could not download {path} from {repo_id}: {exc}") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".part")
    temporary.write_bytes(content)
    temporary.replace(destination)
    return destination


def _split_candidates(split: str) -> tuple[str, ...]:
    return (
        f"data/{split}.jsonl",
        f"{split}.jsonl",
        f"data/{split}.parquet",
        f"{split}.parquet",
    )


def _load_hub(
    source: str,
    *,
    split: str | None,
    revision: str | None,
    hf_file: str | None,
    field_map: FieldMap,
    cache_root: Path | None,
    refresh: bool,
    where: Mapping[str, str] | None = None,
) -> Dataset:
    repo_id, requested = _parse_hub_source(source, revision)
    requested = requested or "main"
    resolved = _resolve_hub_revision(repo_id, requested)
    root = (
        (cache_root or cache_dir())
        / "datasets"
        / repo_id.replace("/", "--")
        / re.sub(r"[^A-Za-z0-9_.-]+", "-", resolved or requested)
    )
    collector = _Collector(field_map, where)
    fetch_revision = resolved or requested

    if hf_file:
        path = _fetch_hub_file(repo_id, fetch_revision, hf_file, root=root, refresh=refresh)
        if path is None:
            raise DatasetError(f"{repo_id}@{requested}: file not found: {hf_file}")
        collector.add_file(path, f"hf:{repo_id}/{hf_file}", fallback_split=None)
        examples = _filter_split(collector.examples, split, origin=f"hf:{repo_id}/{hf_file}")
        label = split or "all"
    else:
        label = split or "test"
        wanted = SPLITS if label == "all" else (label,)
        for name in wanted:
            for candidate in _split_candidates(name):
                path = _fetch_hub_file(repo_id, fetch_revision, candidate, root=root, refresh=refresh)
                if path is not None:
                    collector.add_file(path, f"hf:{repo_id}/{candidate}", fallback_split=name)
                    break
            else:
                if label != "all":
                    raise DatasetError(
                        f"{repo_id}@{requested}: no file for split {name!r} "
                        f"(tried {', '.join(_split_candidates(name))}); "
                        "use --hf-file for a different layout"
                    )
        examples = collector.examples

    if not examples:
        raise DatasetError(
            f"{repo_id}@{requested}: no examples found for split {label!r}" + _filter_hint(collector)
        )
    return Dataset(
        examples=tuple(examples),
        info=DatasetInfo(
            source=f"hf:{repo_id}",
            kind="hub",
            split=label,
            revision=requested,
            resolved_revision=resolved,
            files=tuple(collector.files),
            generated_ids=collector.generated_ids,
            filters=collector.filters,
        ),
    )


# ----------------------------------------------------------------------------
# Local sources
# ----------------------------------------------------------------------------


def _filter_split(examples: list[Example], split: str | None, *, origin: str) -> list[Example]:
    if split is None or split == "all":
        return examples
    selected = [example for example in examples if example.split == split]
    if not selected:
        raise DatasetError(
            f"{origin}: no rows with split {split!r}; drop --split to load every row of the file"
        )
    return selected


def _load_directory(
    path: Path, *, split: str | None, field_map: FieldMap, where: Mapping[str, str] | None = None
) -> Dataset:
    label = split or "test"
    wanted = SPLITS if label == "all" else (label,)
    collector = _Collector(field_map, where)
    for name in wanted:
        found = next(
            (path / candidate for candidate in _split_candidates(name) if (path / candidate).is_file()),
            None,
        )
        if found is None:
            if label != "all":
                raise DatasetError(
                    f"{path}: no file for split {name!r} (tried {', '.join(_split_candidates(name))})"
                )
            continue
        collector.add_file(found, str(found), fallback_split=name)
    if not collector.examples:
        raise DatasetError(f"{path}: no examples found for split {label!r}" + _filter_hint(collector))
    return Dataset(
        examples=tuple(collector.examples),
        info=DatasetInfo(
            source=str(path),
            kind="directory",
            split=label,
            files=tuple(collector.files),
            generated_ids=collector.generated_ids,
            filters=collector.filters,
        ),
    )


def _load_file(
    path: Path, *, split: str | None, field_map: FieldMap, where: Mapping[str, str] | None = None
) -> Dataset:
    collector = _Collector(field_map, where)
    collector.add_file(path, str(path), fallback_split=None)
    examples = _filter_split(collector.examples, split, origin=str(path))
    if not examples:
        raise DatasetError(f"{path}: no examples found" + _filter_hint(collector))
    return Dataset(
        examples=tuple(examples),
        info=DatasetInfo(
            source=str(path),
            kind="file",
            split=split or "all",
            files=tuple(collector.files),
            generated_ids=collector.generated_ids,
            filters=collector.filters,
        ),
    )


def load_dataset(
    source: str | os.PathLike[str],
    *,
    split: str | None = None,
    revision: str | None = None,
    hf_file: str | None = None,
    field_map: FieldMap | None = None,
    cache_root: Path | None = None,
    refresh: bool = False,
    where: Mapping[str, str] | None = None,
) -> Dataset:
    """Load labelled examples from a file, a directory or the Hugging Face Hub.

    Args:
        source: A path, or ``hf:owner/name[@revision]``.
        split: ``train``, ``validation``, ``test`` or ``all``. Defaults to
            ``test`` for directories and Hub datasets, and to every row for a
            single file.
        revision: Branch, tag or commit of a Hub dataset. Pin a commit to make a
            published result reproducible.
        hf_file: Exact file inside a Hub dataset, for repositories that do not
            use the ``data/<split>.jsonl`` layout.
        field_map: Column mapping; see :class:`FieldMap`.
        cache_root: Where Hub downloads are cached.
        refresh: Download again even if a cached copy exists.
        where: Keep only the rows whose columns equal these values, compared as
            text: ``{"type": "safe"}`` keeps rows with ``type == "safe"``.
    """

    if split is not None and split != "all" and split not in SPLITS:
        raise DatasetError(f"split must be one of {', '.join(SPLITS)} or all")
    mapping = field_map or FieldMap()
    text = os.fspath(source)
    if text.startswith(_HUB_PREFIXES):
        return _load_hub(
            text,
            split=split,
            revision=revision,
            hf_file=hf_file,
            field_map=mapping,
            cache_root=cache_root,
            refresh=refresh,
            where=where,
        )
    if revision or hf_file:
        raise DatasetError("--revision and --hf-file only apply to hf: sources")
    path = Path(text).expanduser()
    if path.is_dir():
        return _load_directory(path, split=split, field_map=mapping, where=where)
    if path.is_file():
        return _load_file(path, split=split, field_map=mapping, where=where)
    raise DatasetError(f"dataset source does not exist: {path}")


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Findings of a structural check. ``errors`` make results untrustworthy."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    stats: Mapping[str, Any]

    @property
    def valid(self) -> bool:
        return not self.errors


def _preview(items: Sequence[str], limit: int = 5) -> str:
    shown = ", ".join(items[:limit])
    return shown if len(items) <= limit else f"{shown} and {len(items) - limit} more"


def _normalized_text(text: str) -> str:
    return " ".join(text.casefold().split())


def validate_examples(examples: Sequence[Example], *, generated_ids: int = 0) -> ValidationResult:
    """Check ids, label consistency and pair structure.

    Errors: duplicate ids, and the same text carrying both labels.
    Warnings: everything that limits what can be measured (no language tags,
    incomplete pairs, a missing class, duplicated texts).
    """

    errors: list[str] = []
    warnings: list[str] = []

    id_counts = Counter(example.id for example in examples)
    duplicate_ids = sorted(value for value, count in id_counts.items() if count > 1)
    if duplicate_ids:
        errors.append(
            f"{len(duplicate_ids)} duplicate ids ({_preview(duplicate_ids)}); "
            "if the ids restart in every split, load with --id-field auto"
        )

    by_text: dict[str, list[Example]] = defaultdict(list)
    for example in examples:
        by_text[_normalized_text(example.text)].append(example)
    conflicts = [rows for rows in by_text.values() if len({row.label for row in rows}) > 1]
    if conflicts:
        sample = [f"{rows[0].id}/{rows[1].id}" for rows in conflicts]
        errors.append(
            f"{len(conflicts)} texts appear with both labels ({_preview(sample)}); "
            "the same input cannot be an attack and benign"
        )
    repeated = sum(
        len(rows) - 1 for rows in by_text.values() if len(rows) > 1 and len({r.label for r in rows}) == 1
    )
    if repeated:
        warnings.append(f"{repeated} rows repeat the text of another row with the same label")

    pair_rows: dict[tuple[str, str], list[Example]] = defaultdict(list)
    for example in examples:
        if example.pair_key is not None:
            pair_rows[example.pair_key].append(example)
    complete = 0
    incomplete: list[str] = []
    cross_split: list[str] = []
    for (pair_id, language), rows in sorted(pair_rows.items()):
        if len(rows) == 2 and {row.label for row in rows} == {0, 1}:
            complete += 1
            if len({row.split for row in rows}) > 1:
                cross_split.append(pair_id)
        else:
            incomplete.append(pair_id if language == "unknown" else f"{pair_id} [{language}]")
    if incomplete:
        warnings.append(
            f"{len(incomplete)} pair ids are not one benign row plus one attack row "
            f"and are left out of the pair analysis ({_preview(incomplete)})"
        )
    if cross_split:
        warnings.append(
            f"{len(cross_split)} pairs have their two rows in different splits ({_preview(cross_split)})"
        )

    languages_per_pair: dict[str, set[str]] = defaultdict(set)
    for pair_id, language in pair_rows:
        languages_per_pair[pair_id].add(language)
    parallel = sum(1 for languages in languages_per_pair.values() if len(languages) > 1)

    attacks = sum(example.label for example in examples)
    benign = len(examples) - attacks
    if attacks == 0:
        warnings.append("no attack rows: recall cannot be measured")
    if benign == 0:
        warnings.append("no benign rows: the false-positive rate cannot be measured")
    if not pair_rows:
        warnings.append("no pair ids: the pair analysis is skipped")
    untagged = sum(1 for example in examples if example.language == "unknown")
    if untagged:
        warnings.append(
            f"{untagged} rows have no language tag and are reported as 'unknown' "
            "(use --default-language if the whole dataset is in one language)"
        )
    if generated_ids:
        warnings.append(f"{generated_ids} rows had no id; ids were generated from row order")

    language_stats: dict[str, dict[str, int]] = {}
    for example in examples:
        entry = language_stats.setdefault(example.language, {"attacks": 0, "benign": 0})
        entry["attacks" if example.label == 1 else "benign"] += 1
    lengths = [len(example.text) for example in examples]
    families = Counter(example.attack_family for example in examples if example.label == 1)
    stats: dict[str, Any] = {
        "examples": len(examples),
        "attacks": attacks,
        "benign": benign,
        "languages": dict(sorted(language_stats.items())),
        "splits": dict(sorted(Counter(example.split or "unspecified" for example in examples).items())),
        "attack_families": dict(sorted((str(name), count) for name, count in families.items())),
        "pairs": {
            "complete": complete,
            "incomplete": len(incomplete),
            "in_several_languages": parallel,
        },
        "text_chars": (
            {"min": min(lengths), "median": int(median(lengths)), "max": max(lengths)} if lengths else None
        ),
    }
    return ValidationResult(errors=tuple(errors), warnings=tuple(warnings), stats=stats)
