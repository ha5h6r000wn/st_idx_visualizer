import pathlib
import sys

import pandas as pd
import pytest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config  # noqa: E402
from data_preparation.data_fetcher import (  # noqa: E402
    CANONICAL_COL_MAPPINGS,
    DATASET_SCHEMAS,
    fetch_data_from_local,
)


@pytest.mark.schema
@pytest.mark.parametrize(
    "table_name",
    [
        "CN_BOND_YIELD",
        "A_IDX_VAL",
        "EDB",
        "SHIBOR_PRICES",
    ],
)
def test_fetch_data_from_local_respects_dataset_schema(table_name: str) -> None:
    """fetch_data_from_local MUST respect dataset schema definitions for core tables."""
    latest_date = "99991231"

    df = fetch_data_from_local(latest_date=latest_date, table_name=table_name)
    assert isinstance(df, pd.DataFrame)

    # It is valid for CSV snapshots to be empty in some environments, but when
    # data is present it MUST respect the declared schema.
    if df.empty:
        return

    schema = DATASET_SCHEMAS[table_name]
    dtypes = schema["dtypes"]

    # All declared columns MUST exist on the frame.
    missing_cols = set(dtypes.keys()) - set(df.columns)
    assert not missing_cols, f"Missing columns for {table_name}: {missing_cols}"

    # Date column MUST exist and index must be monotonically decreasing after fetch.
    date_col = schema["date_col"]
    assert date_col in df.columns
    assert df[date_col].is_monotonic_decreasing

    # Canonical English aliases MUST be present when declared.
    canonical_cols = CANONICAL_COL_MAPPINGS.get(table_name, {})
    for canonical, source in canonical_cols.items():
        assert source in df.columns
        assert canonical in df.columns

    # Column dtypes MUST be compatible with the declared mapping.
    for col, expected_dtype in dtypes.items():
        series = df[col]
        if expected_dtype is float:
            # Allow NaNs but require numeric dtype.
            assert pd.api.types.is_numeric_dtype(series), f"{table_name}.{col} expected numeric dtype"
        elif expected_dtype is str:
            assert pd.api.types.is_string_dtype(series), f"{table_name}.{col} expected string dtype"

