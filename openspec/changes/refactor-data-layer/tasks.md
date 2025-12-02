## 1. Implementation
- [ ] 1.1 Add dataset metadata and a CSV `DataSource` implementation with a factory (no DB path), injected instead of global switches.
- [ ] 1.2 Remove `CURRENT_DATA_SOURCE` branching; replace with metadata-driven fetch + filters that emit normalized schemas.
- [ ] 1.3 Normalize column names per dataset (trade_date/code/name/value fields) and expose aliases for existing Chinese labels to keep charts working.
- [ ] 1.4 Delete unused DB session code/config and guard against stale imports.
- [ ] 1.5 Split the bar+line+signal chart helper into prep/render functions and delete stale commented code.
- [ ] 1.6 Update docs/tests: note CSV-only data source and provide a Streamlit smoke-check path.
