## Design

### Goal
Accept Chinese physical headers for `data/csv/index_prices.csv` without breaking existing app code that relies on legacy/raw Wind columns.

### Approach
- Treat the CSV headers as *physical* (Chinese) and keep the app's *raw* contract stable (Wind columns).
- In the `A_IDX_PRICE` schema, declare a `physical_to_raw` mapping:
  - `交易日期` → `TRADE_DT`
  - `证券代码` → `S_INFO_WINDCODE`
  - `证券简称` → `S_INFO_NAME`
  - `收盘价` → `S_DQ_CLOSE`
- During CSV load, materialize the raw Wind columns when they are missing, then reuse the existing canonical alias mechanism to add:
  - `trade_date`, `wind_code`, `wind_name`, `close`

### Non-goals (deferred)
- Migrating strategy/style consumers to use Chinese columns directly.
- Replacing Wind raw columns with canonical English columns as the primary contract.

