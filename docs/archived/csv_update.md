# Archived: CSV update notes

This document is archived. The app-facing CSV contract is summarized in `README.md`.

---

# 1. 保存dev分支的开发进度
git stash save "WIP: feature development"  # WIP = Work In Progress

# 2. 更新CSV
git checkout csv-updates    # 基于main的csv-updates分支
<!-- git reset --hard main    # 将csv-updates重置到main的最新状态 -->
git rebase origin/main

git add data/csv/
git commit -m "chore: update csv" # CSV更新

git checkout main
git fetch origin
git rebase csv-updates      # 合并CSV更新到main
git push origin main            # 只推送main分支

# 3. 返回dev分支，进行代码更新
git checkout dev          # 开发分支
git fetch origin
git rebase origin/main
git stash pop   # 恢复之前的开发更改

git commit -m "feat: xxx" # 代码更新
git checkout main
git merge --no-ff dev    # 合并代码更新到main

# FIXME 更新index_prices时出现了指数中文简称变化的情况，导致数据库内数据出现了不一致，如何修复？增加检测机制，触发数据重跑更新？

---

## App-facing CSV expectations

- Include `data/csv/financial_factors_stocks.csv` when updating CSV snapshots for the Streamlit app.
- Include `data/csv/financial_factors_backtest_nav.csv` when updating CSV snapshots for the Streamlit app.
- Keep CSV headers stable (the app relies on exact column names such as `交易日期` and the strategy signal columns).
- If headers or types change, update the corresponding CSV schema/dtype declarations and tests before merging.

