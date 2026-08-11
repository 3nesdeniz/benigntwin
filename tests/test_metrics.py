from injectbench.metrics import confusion, grouped_confusion, paired_analysis


def test_confusion_basic():
    # true:    1 1 0 0 1
    # pred:    1 0 0 1 1
    c = confusion([1, 1, 0, 0, 1], [1, 0, 0, 1, 1])
    assert (c.tp, c.fp, c.tn, c.fn) == (2, 1, 1, 1)
    assert c.total == 5
    assert round(c.precision, 3) == round(2 / 3, 3)
    assert round(c.recall, 3) == round(2 / 3, 3)
    assert round(c.fpr, 3) == 0.5


def test_confusion_perfect():
    c = confusion([1, 0, 1, 0], [1, 0, 1, 0])
    assert c.recall == 1.0
    assert c.fpr == 0.0
    assert c.f1 == 1.0
    assert c.accuracy == 1.0


def test_confusion_empty_edge():
    c = confusion([], [])
    assert c.precision == 0.0 and c.recall == 0.0 and c.accuracy == 0.0


def test_length_mismatch():
    import pytest
    with pytest.raises(ValueError):
        confusion([1, 0], [1])


def test_grouped():
    g = grouped_confusion(
        [1, 1, 0], [1, 0, 0], ["override", "override", "benign"]
    )
    assert g["override"].tp == 1 and g["override"].fn == 1
    assert g["benign"].tn == 1


def test_paired():
    # pair 0: attack caught, benign cleared -> both_correct
    # pair 1: attack missed, benign cleared -> benign_only
    # pair 2: attack caught, benign flagged -> attack_only
    r = paired_analysis([1, 0, 1], [0, 0, 1])
    assert r.pairs == 3
    assert r.both_correct == 1
    assert r.benign_only == 1
    assert r.attack_only == 1
    assert round(r.boundary_accuracy, 3) == round(1 / 3, 3)
