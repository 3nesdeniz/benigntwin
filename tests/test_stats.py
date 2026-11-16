from __future__ import annotations

import pytest

from injectbench.stats import mcnemar_exact, percentile, roc_auc, wilson_interval


def test_wilson_matches_published_values():
    # Reference values for the Wilson score interval (Newcombe 1998, method 3).
    low, high = wilson_interval(81, 263)
    assert low == pytest.approx(0.2553, abs=5e-4)
    assert high == pytest.approx(0.3662, abs=5e-4)
    low, high = wilson_interval(15, 148)
    assert low == pytest.approx(0.0624, abs=5e-4)
    assert high == pytest.approx(0.1605, abs=5e-4)


def test_wilson_zero_events_still_has_an_upper_bound():
    low, high = wilson_interval(0, 60)
    assert low == 0.0
    assert high == pytest.approx(0.0602, abs=5e-4)
    low, high = wilson_interval(60, 60)
    assert high == 1.0
    assert low == pytest.approx(1 - 0.0602, abs=5e-4)


def test_wilson_interval_contains_the_estimate_and_narrows_with_more_data():
    small = wilson_interval(5, 20)
    large = wilson_interval(500, 2000)
    assert small[0] < 0.25 < small[1]
    assert large[0] < 0.25 < large[1]
    assert (large[1] - large[0]) < (small[1] - small[0])
    assert wilson_interval(5, 20, 0.99)[1] > small[1]


def test_wilson_edge_cases():
    assert wilson_interval(0, 0) is None
    with pytest.raises(ValueError):
        wilson_interval(3, 2)
    with pytest.raises(ValueError):
        wilson_interval(1, 2, confidence=1.0)


def test_mcnemar_exact_known_values():
    assert mcnemar_exact(0, 0) is None
    assert mcnemar_exact(5, 5) == 1.0
    # 10 discordant items, all in one direction: 2 * 0.5**10
    assert mcnemar_exact(10, 0) == pytest.approx(2 / 1024)
    assert mcnemar_exact(0, 10) == pytest.approx(2 / 1024)
    # 1 vs 9: 2 * (C(10,0) + C(10,1)) / 2**10
    assert mcnemar_exact(1, 9) == pytest.approx(2 * 11 / 1024)
    with pytest.raises(ValueError):
        mcnemar_exact(-1, 2)


def test_roc_auc():
    assert roc_auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0]) == 1.0
    assert roc_auc([0.1, 0.2, 0.8, 0.9], [1, 1, 0, 0]) == 0.0
    assert roc_auc([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0]) == 0.5
    # one of four attack/benign comparisons is lost
    assert roc_auc([0.9, 0.4, 0.6, 0.1], [1, 1, 0, 0]) == pytest.approx(0.75)
    assert roc_auc([0.9, 0.8], [1, 1]) is None
    with pytest.raises(ValueError):
        roc_auc([0.1], [1, 0])


def test_percentile():
    assert percentile([], 0.5) is None
    assert percentile([3.0], 0.95) == 3.0
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5
    assert percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.95) == pytest.approx(4.8)
    with pytest.raises(ValueError):
        percentile([1.0], 1.5)
