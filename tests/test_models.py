from __future__ import annotations

import math

import pytest

from benigntwin.models import (
    Example,
    LabelError,
    ModelError,
    Prediction,
    Record,
    normalize_family,
    normalize_label,
    normalize_language,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, 1), (0, 0), (True, 1), (False, 0), (1.0, 1), (0.0, 0),
        ("1", 1), ("0", 0), ("attack", 1), ("Injection", 1), ("JAILBREAK", 1),
        ("prompt-injection", 1), ("Prompt Injection", 1), ("unsafe", 1), (" malicious ", 1),
        ("benign", 0), ("SAFE", 0), ("legitimate", 0), ("allowed", 0),
    ],
)  # fmt: skip
def test_normalize_label_accepts_common_spellings(value, expected):
    assert normalize_label(value) == expected


@pytest.mark.parametrize("value", ["harmful", "maybe", "", 2, -1, 0.5, None, [1], "label_1"])
def test_normalize_label_never_guesses(value):
    with pytest.raises(LabelError):
        normalize_label(value)


def test_language_is_never_assumed_to_be_english():
    assert normalize_language(None) == "unknown"
    assert normalize_language("  ") == "unknown"
    assert normalize_language("TR") == "tr"
    assert normalize_language("pt_BR") == "pt-br"


def test_family_placeholders_on_benign_rows_become_none():
    for placeholder in ("none", "benign", "", None, "Unknown", "N/A"):
        assert normalize_family(placeholder, label=0) is None
    assert normalize_family("approval_bypass", label=0) == "approval_bypass"
    assert normalize_family(None, label=1) == "unknown"
    assert normalize_family("prompt_leak", label=1) == "prompt_leak"


def test_example_rejects_bad_rows():
    with pytest.raises(ModelError):
        Example(id="x", text="   ", label=0)
    with pytest.raises(ModelError):
        Example(id="x", text="hello", label=2)


def test_pair_key_is_scoped_to_the_language():
    english = Example(id="a", text="t", label=1, pair_id="p1", language="en")
    turkish = Example(id="b", text="t", label=1, pair_id="p1", language="tr")
    assert english.pair_key == ("p1", "en")
    assert turkish.pair_key == ("p1", "tr")
    assert Example(id="c", text="t", label=0).pair_key is None


def test_detector_input_carries_no_ground_truth():
    example = Example(
        id="a", text="hello", label=1, attack_family="prompt_leak", pair_id="p1",
        language="en", fields={"category": "prompt_injection", "label": 1},
    )  # fmt: skip
    assert example.detector_input() == {"id": "a", "text": "hello"}


def test_example_get_reads_known_and_extra_fields():
    example = Example(id="a", text="t", label=1, language="tr", fields={"source_context": "tool"})
    assert example.get("language") == "tr"
    assert example.get("source_context") == "tool"
    assert example.get("missing") is None


@pytest.mark.parametrize(
    ("value", "label", "score"),
    [
        (1, 1, None), (False, 0, None), ("attack", 1, None), (0.25, None, 0.25),
        ({"label": "benign"}, 0, None), ({"score": 0.9}, None, 0.9),
        ({"prediction": 1, "score": 0.7}, 1, 0.7), ({"predicted_label": "safe"}, 0, None),
    ],
)  # fmt: skip
def test_prediction_from_value_shapes(value, label, score):
    prediction = Prediction.from_value("x", value)
    assert (prediction.label, prediction.score) == (label, score)


def test_prediction_prefers_the_detector_output_over_a_truth_column():
    # A file with both the ground truth ("label") and the output ("prediction")
    # must be scored on the output.
    prediction = Prediction.from_value("x", {"label": 1, "prediction": 0})
    assert prediction.label == 0


@pytest.mark.parametrize(
    "value", [None, {}, {"score": 1.5}, {"score": "high"}, 2.0, math.nan, {"score": True}]
)
def test_prediction_from_value_rejects_garbage(value):
    with pytest.raises(ModelError):
        Prediction.from_value("x", value)


def test_decide_modes():
    both = Prediction(id="x", label=0, score=0.9)
    assert both.decide(0.5) == 0  # auto keeps the detector's own decision
    assert both.decide(0.5, decision="label") == 0
    assert both.decide(0.5, decision="score") == 1
    score_only = Prediction(id="x", score=0.5)
    assert score_only.decide(0.5) == 1  # at the threshold counts as flagged
    assert score_only.decide(0.51) == 0
    with pytest.raises(ModelError):
        score_only.decide(0.5, decision="label")
    with pytest.raises(ModelError):
        Prediction(id="x", label=1).decide(0.5, decision="score")
    with pytest.raises(ModelError):
        both.decide(0.5, decision="sometimes")


def test_prediction_validates_ranges():
    with pytest.raises(ModelError):
        Prediction(id="x", label=3)
    with pytest.raises(ModelError):
        Prediction(id="x", score=-0.1)


def test_record_flags():
    example = Example(id="a", text="t", label=0)
    record = Record(example=example, prediction=Prediction(id="a", label=1), predicted=1)
    assert record.flagged and not record.correct
