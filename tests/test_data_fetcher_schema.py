import pathlib
import sys

import pandas as pd
import pytest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config, param_cls  # noqa: E402
from data_preparation.data_fetcher import (  # noqa: E402
    CANONICAL_COL_MAPPINGS,
    DATASET_SCHEMAS,
    FINANCIAL_FACTORS_STOCKS_SCHEMA,
    INDEX_PRICE_SCHEMA,
    fetch_data_from_local,
    fetch_financial_factors_stocks_from_local,
    fetch_index_data_from_local,
    read_csv_data,
)
from config import style_config  # noqa: E402


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


@pytest.mark.schema
def test_wind_idx_col_param_matches_index_price_schema() -> None:
    """WindIdxColParam MUST align with the canonical INDEX_PRICE schema."""
    schema = INDEX_PRICE_SCHEMA
    canonical_cols = schema["canonical_cols"]

    idx_cols = param_cls.WindIdxColParam()

    # Date column MUST be consistent between the schema and the column param.
    assert schema["date_col"] == idx_cols.dt_col
    assert canonical_cols["trade_date"] == idx_cols.dt_col

    # Code/name/price columns MUST match the canonical mapping.
    assert canonical_cols["wind_code"] == idx_cols.code_col
    assert canonical_cols["wind_name"] == idx_cols.name_col
    assert canonical_cols["close"] == idx_cols.price_col


@pytest.mark.schema
def test_fetch_index_data_from_local_respects_index_price_schema() -> None:
    """fetch_index_data_from_local MUST respect INDEX_PRICE schema when data is present."""
    latest_date = "99991231"

    # Reuse the same index universe as the style and stg_idx pages to keep this
    # test aligned with real consumers.
    style_idx_codes = tuple(style_config.STYLE_IDX_CODES.values())
    stg_and_bench_codes = tuple(config.STG_IDX_CODES + config.BENCH_IDX_CODES)
    wind_idx_param = param_cls.WindListedSecParam(
        wind_codes=style_idx_codes + stg_and_bench_codes,
        start_date=config.START_DT,
        sql_param=param_cls.SqlParam(sql_name=config.IDX_PRICE_SQL_NAME),
    )

    df = fetch_index_data_from_local(latest_date=latest_date, _config=wind_idx_param)
    assert isinstance(df, pd.DataFrame)

    if df.empty:
        # Allow empty snapshots in some environments; invariants only apply when data exists.
        return

    schema = INDEX_PRICE_SCHEMA
    dtypes = schema["dtypes"]

    # All declared columns MUST exist on the frame.
    missing_cols = set(dtypes.keys()) - set(df.columns)
    assert not missing_cols, f"Missing columns for A_IDX_PRICE: {missing_cols}"

    # Date column MUST exist and be monotonically decreasing.
    date_col = schema["date_col"]
    assert date_col in df.columns
    assert df[date_col].is_monotonic_decreasing

    # Canonical English aliases MUST be present alongside the CSV columns.
    canonical_cols = CANONICAL_COL_MAPPINGS["A_IDX_PRICE"]
    for canonical, source in canonical_cols.items():
        assert source in df.columns
        assert canonical in df.columns

    # Column dtypes MUST be compatible with the declared mapping.
    for col, expected_dtype in dtypes.items():
        series = df[col]
        if expected_dtype is float:
            assert pd.api.types.is_numeric_dtype(series), f"A_IDX_PRICE.{col} expected numeric dtype"
        elif expected_dtype is str:
            assert pd.api.types.is_string_dtype(series), f"A_IDX_PRICE.{col} expected string dtype"


@pytest.mark.schema
def test_read_csv_data_coerces_dirty_numeric_values(tmp_path, monkeypatch, capsys) -> None:
    """read_csv_data MUST tolerate dirty numeric cells and coerce them to NaN."""
    table_name = "A_IDX_VAL"
    csv_name = "dirty_index_valuations.csv"
    csv_path = tmp_path / csv_name

    csv_path.write_text(
        "id,交易日期,证券代码,证券简称,日换手率,市盈率,更新时间\n"
        "1,20250101,000300.SH,沪深300,0.5087,12.5449,2025-03-24 11:19:33.910246\n"
        "2,20250102,000300.SH,沪深300,--,null,2025-03-24 11:19:33.910246\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(config, "CSV_DATA_DIR", str(tmp_path))
    monkeypatch.setitem(config.CSV_FILE_MAPPING, table_name, csv_name)

    df = read_csv_data(table_name)
    assert not df.empty
    assert pd.api.types.is_numeric_dtype(df["日换手率"])
    assert pd.api.types.is_numeric_dtype(df["市盈率"])
    assert pd.isna(df.loc[1, "日换手率"])
    assert pd.isna(df.loc[1, "市盈率"])

    out = capsys.readouterr().out
    assert "Warning:" in out
    assert "column 日换手率" in out
    assert "column 市盈率" in out


@pytest.mark.schema
def test_fetch_financial_factors_stocks_from_local_respects_schema() -> None:
    """Financial-factors stock-pool loader MUST respect the declared dataset schema."""
    latest_date = "99991231"

    df = fetch_financial_factors_stocks_from_local(latest_date=latest_date)
    assert isinstance(df, pd.DataFrame)

    if df.empty:
        return

    schema = FINANCIAL_FACTORS_STOCKS_SCHEMA
    dtypes = schema["dtypes"]

    missing_cols = set(dtypes.keys()) - set(df.columns)
    assert not missing_cols, f"Missing columns for {schema['table_name']}: {missing_cols}"

    date_col = schema["date_col"]
    assert date_col in df.columns
    assert df[date_col].is_monotonic_decreasing

    canonical_cols = CANONICAL_COL_MAPPINGS.get(schema["table_name"], {})
    for canonical, source in canonical_cols.items():
        assert source in df.columns
        assert canonical in df.columns

    for col, expected_dtype in dtypes.items():
        series = df[col]
        if expected_dtype is float:
            assert pd.api.types.is_numeric_dtype(series), f"{schema['table_name']}.{col} expected numeric dtype"
        elif expected_dtype is str:
            assert pd.api.types.is_string_dtype(series), f"{schema['table_name']}.{col} expected string dtype"
