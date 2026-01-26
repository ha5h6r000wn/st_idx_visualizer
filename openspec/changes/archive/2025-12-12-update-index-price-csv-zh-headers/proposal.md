# Change: Update A_IDX_PRICE CSV Chinese headers (stage 1)

## Why
`data/csv/index_prices.csv` headers were unified to Chinese. The app's CSV loader for `A_IDX_PRICE` previously expected legacy Wind raw headers (`TRADE_DT`, `S_INFO_WINDCODE`, `S_INFO_NAME`, `S_DQ_CLOSE`), which breaks CSV loading and schema validation.

## What Changes
- Update the declared CSV dtype mapping for `A_IDX_PRICE` to match the Chinese physical headers (`交易日期`, `证券代码`, `证券简称`, `收盘价`).
- Teach the CSV loader to materialize legacy/raw Wind columns from the Chinese physical headers via a schema-declared mapping, keeping downstream consumers stable.
- Preserve the existing public DataFrame contract for the app:
  - Strategy/style pages continue using `WindIdxColParam` defaults (Wind raw columns),
  - Canonical English aliases (`trade_date`, `wind_code`, `wind_name`, `close`) remain available.

## Impact
- Affected specs: `data-access`
- Affected code:
  - `config/config.py` (`CSV_DTYPE_MAPPING["A_IDX_PRICE"]`)
  - `data_preparation/data_fetcher.py` (`INDEX_PRICE_SCHEMA`, CSV load normalization)
- Validation:
  - `python -m pytest -m schema`
  - `python -m pytest`

