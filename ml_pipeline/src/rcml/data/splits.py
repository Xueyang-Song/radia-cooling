from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rcml.data.dataset import LoadedDataset


SPLIT_MODES = ["random", "holdout_combo", "holdout_thickness_tail"]


@dataclass(frozen=True)
class DatasetSplit:
    train_indices: np.ndarray
    test_indices: np.ndarray
    summary: dict[str, object]


def available_split_modes() -> list[str]:
    return list(SPLIT_MODES)


def make_dataset_split(
    dataset: LoadedDataset,
    split_mode: str,
    test_size: float,
    random_seed: int,
) -> DatasetSplit:
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be between 0 and 1.")

    normalized = split_mode.lower()
    count = len(dataset.records)
    if count < 2:
        raise ValueError("At least two samples are required to make a train/test split.")

    target_test_count = max(1, int(round(count * test_size)))
    target_test_count = min(target_test_count, count - 1)

    if normalized == "random":
        return _random_split(count=count, target_test_count=target_test_count, random_seed=random_seed)
    if normalized == "holdout_combo":
        return _holdout_combo_split(dataset=dataset, target_test_count=target_test_count, random_seed=random_seed)
    if normalized == "holdout_thickness_tail":
        return _holdout_thickness_tail_split(dataset=dataset, target_test_count=target_test_count)
    raise ValueError(f"Unsupported split mode: {split_mode}")


def _random_split(count: int, target_test_count: int, random_seed: int) -> DatasetSplit:
    rng = np.random.default_rng(random_seed)
    indices = rng.permutation(count)
    test_indices = np.sort(indices[:target_test_count])
    train_indices = np.sort(indices[target_test_count:])
    return DatasetSplit(
        train_indices=train_indices,
        test_indices=test_indices,
        summary={
            "split_mode": "random",
            "train_count": int(train_indices.size),
            "test_count": int(test_indices.size),
            "random_seed": int(random_seed),
        },
    )


def _holdout_combo_split(
    dataset: LoadedDataset,
    target_test_count: int,
    random_seed: int,
) -> DatasetSplit:
    combo_to_indices: dict[tuple[str, ...], list[int]] = {}
    for index, record in enumerate(dataset.records):
        combo = tuple(str(item) for item in record["layer_materials"])
        combo_to_indices.setdefault(combo, []).append(index)

    combos = list(combo_to_indices)
    if len(combos) < 2:
        raise ValueError("holdout_combo requires at least two unique material combinations.")

    rng = np.random.default_rng(random_seed)
    rng.shuffle(combos)

    held_out_combos: list[tuple[str, ...]] = []
    test_indices_list: list[int] = []

    for combo in combos[:-1]:
        held_out_combos.append(combo)
        test_indices_list.extend(combo_to_indices[combo])
        if len(test_indices_list) >= target_test_count:
            break

    if not held_out_combos:
        held_out_combos.append(combos[0])
        test_indices_list.extend(combo_to_indices[combos[0]])

    held_out_set = set(held_out_combos)
    train_indices_list = [
        index
        for combo, indices in combo_to_indices.items()
        if combo not in held_out_set
        for index in indices
    ]
    if not train_indices_list:
        raise ValueError("holdout_combo left no training samples; generate more combinations first.")

    test_indices = np.asarray(sorted(set(test_indices_list)), dtype=np.int64)
    train_indices = np.asarray(sorted(train_indices_list), dtype=np.int64)

    return DatasetSplit(
        train_indices=train_indices,
        test_indices=test_indices,
        summary={
            "split_mode": "holdout_combo",
            "train_count": int(train_indices.size),
            "test_count": int(test_indices.size),
            "held_out_combo_count": len(held_out_combos),
            "held_out_combos": [list(combo) for combo in held_out_combos],
            "random_seed": int(random_seed),
        },
    )


def _holdout_thickness_tail_split(dataset: LoadedDataset, target_test_count: int) -> DatasetSplit:
    total_thickness = np.asarray(
        [float(record["total_thickness_nm"]) for record in dataset.records],
        dtype=np.float64,
    )
    order = np.argsort(total_thickness)
    test_indices = np.sort(order[-target_test_count:])
    train_indices = np.sort(order[:-target_test_count])
    if train_indices.size == 0:
        raise ValueError("holdout_thickness_tail left no training samples.")

    cutoff = float(total_thickness[test_indices].min())
    return DatasetSplit(
        train_indices=train_indices,
        test_indices=test_indices,
        summary={
            "split_mode": "holdout_thickness_tail",
            "train_count": int(train_indices.size),
            "test_count": int(test_indices.size),
            "cutoff_total_thickness_nm": cutoff,
        },
    )