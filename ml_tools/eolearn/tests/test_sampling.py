"""
Credits:
Copyright (c) 2017-2022 Matej Aleksandrov, Matej Batič, Grega Milčinski, Domagoj Korais, Matic Lubej (Sinergise)
Copyright (c) 2017-2022 Žiga Lukšič, Devis Peressutti, Nejc Vesel, Jovan Višnjić, Anže Zupanc (Sinergise)
Copyright (c) 2017-2019 Blaž Sovdat, Andrej Burja (Sinergise)

This source code is licensed under the MIT license found in the LICENSE
file in the root directory of this source tree.
"""
import copy
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from pytest import approx
from shapely.geometry import Point, Polygon

from eolearn.core import EOPatch, FeatureType
from eolearn.ml_tools import BlockSamplingTask, FractionSamplingTask, GridSamplingTask, sample_by_values
from eolearn.ml_tools.sampling import expand_to_grids, random_point_in_triangle


@pytest.mark.parametrize(
    "triangle, expected_points",
    [
        (
            Polygon([[-10, -12], [5, 10], [15, 4]]),
            [Point(7.057238842063997, 5.037835974428286), Point(10.360934995972169, 4.508212300648985)],
        ),
        (
            Polygon([[110, 112], [117, 102], [115, 104]]),
            [Point(115.38602941857646, 103.97472742532676), Point(115.19386890346114, 104.02631432574218)],
        ),
        (
            Polygon([[0, 0], [5, 12], [15, 4]]),
            [Point(8.259761655074744, 7.46815417512301), Point(11.094879093316592, 5.949786169595648)],
        ),
    ],
)
def test_random_point_in_triangle_generator(triangle: Polygon, expected_points: List[Point]) -> None:
    generator = np.random.default_rng(seed=42)
    points = [random_point_in_triangle(triangle, generator) for _ in range(2)]
    assert all(point == expected for point, expected in zip(points, expected_points))


@pytest.mark.parametrize(
    "triangle",
    [
        (Polygon([[-10, -12], [5, 10], [15, 4]])),
        (Polygon([[110, 112], [117, 102], [115, 104]])),
        (Polygon([[0, 0], [5, 12], [15, 4]])),
    ],
)
def test_random_point_in_triangle_interior(triangle: Polygon) -> None:
    points = [random_point_in_triangle(triangle) for _ in range(1000)]
    assert all(triangle.contains(point) for point in points)


@pytest.fixture(name="small_image")
def small_image_fixture() -> np.ndarray:
    image_size = 100, 75
    image = np.zeros(image_size, dtype=np.uint8)
    image[40:60, 40:60] = 1
    image[50:80, 55:70] = 2
    return image


@pytest.mark.parametrize(
    "image, n_samples",
    [
        (np.ones((100,)), {1: 100}),
        (np.ones((100, 100, 3)), {1: 100}),
        (np.ones((100, 100)), {2: 100}),
        (np.ones((100, 100)), {1: 10001}),
    ],
)
def test_sample_by_values_errors(image: np.ndarray, n_samples: Dict[int, int]) -> None:
    rng = np.random.default_rng()
    with pytest.raises(ValueError):
        sample_by_values(image, n_samples, rng=rng)


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize(
    "n_samples, replace",
    [
        ({0: 100, 1: 200, 2: 30}, False),
        ({1: 200}, False),
        ({0: 100, 2: 30000}, True),
    ],
)
def test_sample_by_values(small_image: np.ndarray, seed: int, n_samples: Dict[int, int], replace: bool) -> None:
    rng = np.random.default_rng(seed)

    rows, cols = sample_by_values(small_image, n_samples, rng=rng, replace=replace)
    labels = small_image[rows, cols]

    expected_n_samples = sum(n_samples.values())
    assert len(labels) == expected_n_samples, "Incorrect number of samples"
    assert len(rows) == expected_n_samples, "Incorrect number of samples"
    assert len(cols) == expected_n_samples, "Incorrect number of samples"

    # test number of samples per value is correct
    for value, amount in n_samples.items():
        assert np.sum(labels == value) == amount, f"Incorrect amount of samples for value {value}"


@pytest.mark.parametrize("sample_size", [(1, 1), (2, 3), (10, 11)])
def test_expand_to_grids(sample_size: Tuple[int, int]) -> None:
    rows = np.array([1, 1, 2, 3, 4])
    columns = np.array([2, 3, 1, 1, 4])

    row_grid, column_grid = expand_to_grids(rows, columns, sample_size=sample_size)

    expected_shape = sample_size[0] * rows.size, sample_size[1]
    assert row_grid.shape == expected_shape
    assert column_grid.shape == expected_shape


@pytest.mark.parametrize("seed", list(range(5)))
@pytest.mark.parametrize("amount", [100, 5231, 0.4, 0])
def test_object_sampling_task(small_image: np.ndarray, seed: int, amount: int) -> None:
    t, h, w, d = 10, *small_image.shape, 5
    eop = EOPatch()
    eop.data["bands"] = np.arange(t * h * w * d).reshape(t, h, w, d)
    eop.mask_timeless["raster"] = small_image.reshape(small_image.shape + (1,))

    task = BlockSamplingTask(
        [(FeatureType.DATA, "bands", "SAMPLED_DATA"), (FeatureType.MASK_TIMELESS, "raster", "SAMPLED_LABELS")],
        amount=amount,
        mask_of_samples=(FeatureType.MASK_TIMELESS, "sampling_mask"),
    )

    task.execute(eop, seed=seed)
    expected_amount = amount if isinstance(amount, int) else round(np.prod(small_image.shape) * amount)

    # assert features, labels and sampled rows and cols are added to eopatch
    assert "SAMPLED_LABELS" in eop.mask_timeless, "Labels not added to eopatch"
    assert "SAMPLED_DATA" in eop.data, "Features not added to eopatch"
    assert "sampling_mask" in eop.mask_timeless, "Mask of sampling not generated"
    # check validity of sampling
    assert eop.data["SAMPLED_DATA"].shape == (t, expected_amount, 1, d), "Incorrect features size"
    assert eop.mask_timeless["SAMPLED_LABELS"].shape == (expected_amount, 1, 1), "Incorrect number of samples"
    assert eop.mask_timeless["sampling_mask"].shape == (h, w, 1), "Sampling mask of incorrect size"

    sampled_uniques, sampled_counts = np.unique(eop.data["SAMPLED_DATA"], return_counts=True)
    masked = eop.mask_timeless["sampling_mask"].squeeze(axis=2) == 1
    masked_uniques, masked_counts = np.unique(eop.data["bands"][:, masked, :], return_counts=True)
    assert_array_equal(sampled_uniques, masked_uniques, err_msg="Sampling mask not correctly describing sampled points")
    assert_array_equal(sampled_counts, masked_counts, err_msg="Sampling mask not correctly describing sampled points")


@pytest.mark.parametrize("seed", range(3))
def test_object_sampling_reproducibility(test_eopatch: EOPatch, seed: int) -> None:
    task = BlockSamplingTask(
        [(FeatureType.DATA, "NDVI", "NDVI_SAMPLED")],
        amount=0.1,
        mask_of_samples=(FeatureType.MASK_TIMELESS, "sampling_mask"),
    )

    eopatch1 = task.execute(copy.copy(test_eopatch), seed=seed)
    eopatch2 = task.execute(copy.copy(test_eopatch), seed=seed)
    eopatch3 = task.execute(copy.copy(test_eopatch), seed=(seed + 1))

    # assert features, labels and sampled rows and cols are added to eopatch
    assert eopatch1 == eopatch2, "Same seed produces different results"
    assert (
        eopatch1.mask_timeless["sampling_mask"] != eopatch3.mask_timeless["sampling_mask"]
    ).any(), "Different seed produces same results"


@pytest.mark.parametrize(
    "fraction, replace",
    [[2, False], [-0.5, True], [{1: 0.5, 3: 0.4, 5: 1.2}, False], [{1: 0.5, 3: -0.4, 5: 1.2}, True], [(1, 0.4), True]],
)
def test_fraction_sampling_errors(fraction: Union[float, Dict[int, float]], replace: bool) -> None:
    with pytest.raises(ValueError):
        FractionSamplingTask(
            [(FeatureType.DATA, "NDVI", "NDVI_SAMPLED")],
            (FeatureType.MASK_TIMELESS, "LULC"),
            fraction=fraction,
            replace=replace,
        )


@pytest.mark.parametrize("seed", range(3))
@pytest.mark.parametrize(
    "fraction, exclude",
    [
        [0.2, None],
        [0.4, [0, 1]],
        [{1: 0.1, 3: 0.4}, None],
        [{2: 0.1, 3: 1, 5: 1}, []],
        [{2: 0.1, 3: 1, 5: 1}, [0, 2]],
    ],
)
def test_fraction_sampling(
    seed: int, fraction: Union[float, Dict[int, float]], exclude: Optional[List], test_eopatch: EOPatch
) -> None:
    task = FractionSamplingTask(
        [(FeatureType.DATA, "NDVI", "NDVI_SAMPLED"), (FeatureType.MASK_TIMELESS, "LULC", "LULC_SAMPLED")],
        (FeatureType.MASK_TIMELESS, "LULC"),
        mask_of_samples=(FeatureType.MASK_TIMELESS, "sampling_mask"),
        fraction=fraction,
        exclude_values=exclude,
    )

    eopatch = task(test_eopatch, seed=seed)

    # Test amount
    assert eopatch.mask_timeless["LULC_SAMPLED"].shape == eopatch.data["NDVI_SAMPLED"].shape[1:]

    # Test mask
    sampled_uniques, sampled_counts = np.unique(eopatch.data["NDVI_SAMPLED"], return_counts=True)
    masked = eopatch.mask_timeless["sampling_mask"].squeeze(axis=2) == 1
    masked_uniques, masked_counts = np.unique(eopatch.data["NDVI"][:, masked], return_counts=True)
    assert_array_equal(sampled_uniques, masked_uniques, err_msg="Sampling mask not correctly describing sampled points")
    assert_array_equal(sampled_counts, masked_counts, err_msg="Sampling mask not correctly describing sampled points")

    # Test balance and inclusion/exclusion
    full_values, full_counts = np.unique(eopatch[(FeatureType.MASK_TIMELESS, "LULC")], return_counts=True)
    sample_values, sample_counts = np.unique(eopatch[(FeatureType.MASK_TIMELESS, "LULC_SAMPLED")], return_counts=True)
    full = dict(zip(full_values, full_counts))
    samples = dict(zip(sample_values, sample_counts))
    exclude = exclude or []  # get rid of pesky None

    assert set(exclude).isdisjoint(set(sample_values)), "Exclusion values were present in sample"

    if isinstance(fraction, float):
        for val, count in full.items():
            if val not in exclude:
                assert samples[val] == approx(count * fraction, abs=1), f"Wrong amount of samples for class {val}."
    else:
        assert set(sample_values).issubset(set(fraction)), "Sample contains values that were not requested"
        for val, count in samples.items():
            assert count == approx(full[val] * fraction[val], abs=1), f"Wrong amount of samples for class {val}."


@pytest.mark.parametrize("seed", range(3))
@pytest.mark.parametrize("fraction", [0.3, {1: 0.1, 4: 0.3}])
def test_fraction_sampling_reproducibility(
    test_eopatch: EOPatch, fraction: Union[float, Dict[int, float]], seed: int
) -> None:
    task = FractionSamplingTask(
        [(FeatureType.DATA, "NDVI", "NDVI_SAMPLED")],
        (FeatureType.MASK_TIMELESS, "LULC"),
        fraction=fraction,
        mask_of_samples=(FeatureType.MASK_TIMELESS, "sampling_mask"),
    )

    eopatch1 = task.execute(copy.copy(test_eopatch), seed=seed)
    eopatch2 = task.execute(copy.copy(test_eopatch), seed=seed)
    eopatch3 = task.execute(copy.copy(test_eopatch), seed=(seed + 1))

    # assert features, labels and sampled rows and cols are added to eopatch
    assert eopatch1 == eopatch2, "Same seed produces different results"
    assert (
        eopatch1.mask_timeless["sampling_mask"] != eopatch3.mask_timeless["sampling_mask"]
    ).any(), "Different seed produces same results"


@pytest.mark.parametrize(
    "sample_size, stride, expected_shape",
    [
        [(1, 1), (1, 1), (68, 100 * 101, 1, 13)],
        [(2, 3), (5, 3), (68, 1320, 3, 13)],
        [(6, 5), (3, 3), (68, 6144, 5, 13)],
    ],
)
def test_grid_sampling_task(
    test_eopatch: EOPatch,
    sample_size: Tuple[int, int],
    stride: Tuple[int, int],
    expected_shape: Tuple[int, int, int, int],
) -> None:
    sample_mask = FeatureType.MASK_TIMELESS, "SAMPLE_MASK"
    task = GridSamplingTask(
        features_to_sample=[
            (FeatureType.DATA, "BANDS-S2-L1C", "SAMPLED_BANDS"),
            (FeatureType.MASK_TIMELESS, "LULC", "LULC"),
        ],
        sample_size=sample_size,
        stride=stride,
        mask_of_samples=sample_mask,
    )
    eopatch = task.execute(test_eopatch)

    assert eopatch.data["SAMPLED_BANDS"].shape == expected_shape
    height, width = expected_shape[1:3]
    assert np.sum(eopatch[sample_mask]) == height * width
