## 1. Implementation
- [x] Update `config.CSV_DTYPE_MAPPING["A_IDX_PRICE"]` to use Chinese physical headers (`交易日期`, `证券代码`, `证券简称`, `收盘价`).
- [x] Add a schema-declared Chinese physical → Wind raw mapping for `A_IDX_PRICE` and materialize the Wind raw columns during CSV load.
- [x] Ensure downstream consumers can continue using Wind raw columns (`TRADE_DT`, `S_INFO_WINDCODE`, `S_INFO_NAME`, `S_DQ_CLOSE`) unchanged.
- [x] Run `python -m pytest -m schema`.
- [x] Run `python -m pytest`.

