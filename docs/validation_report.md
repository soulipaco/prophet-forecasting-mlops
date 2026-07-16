# Validation report

Validation completed locally on 2026-07-17. No commit, push, pull request, deployment, repository
setting, or visibility change was performed.

## Passed

| Check | Command or method | Result |
|---|---|---|
| Dependency resolution | `uv sync --extra test --extra portfolio` | passed; 99-package lock resolved |
| Lint | `uv run ruff check src tests scripts tools` | passed |
| Format | `uv run ruff format --check src tests scripts tools` | passed; 21 files checked |
| Local tests | `uv run pytest -m "not databricks"` | 10 passed |
| Package build | `uv build` | source distribution and wheel built |
| Portfolio validation | `uv run python tools/validate_portfolio.py` | links, assets, evidence hash, and safety rules passed |
| Patch whitespace | `git diff --check` | passed |
| Carousel overflow | presentation `slides_test.py` | passed; no overflow detected |
| Carousel visual QA | individual inspection of all eight 1080 x 1350 renders | passed after correcting three hidden titles |
| Repository visuals | individual inspection of hero, architecture, lifecycle, and forecast PNGs | passed after correcting text collisions |

The deterministic synthetic collection was executed twice while building the visuals. Both runs
returned 4 completed fits, 0 failed fits, 832 forecast rows, and 84 backtest rows. The final forecast
CSV SHA-256 is `9bc7476cd9f6fa7628c38bfb4511a1955af84cc3b5e29d5fd1379b0ab9a293fe`.

## Public-safety scan

The validator scans public text and generated evidence while excluding local environments, build
output, Git state, and local Databricks state. It found zero access-token, workspace-host, email,
local-user-path, stale-placeholder, private-source-story, or unrelated-reference hits. PNG outputs
were rewritten without descriptive metadata.

## Databricks validation boundary

`databricks bundle validate` was attempted for dev, acc, and prd. All three were blocked by a 401
authentication response before configuration validation could complete. The bundle had validated
for all three targets on 2026-07-16, but that earlier external result is not presented as a current
pass. Re-run the commands below after establishing OAuth or workload-identity authentication:

```bash
databricks auth login
databricks bundle validate -t dev
databricks bundle validate -t acc
databricks bundle validate -t prd
```

## Known limits

- The local suite contains unit/contract tests but no real Prophet integration test.
- The synthetic visual proves execution and schema behavior, not forecast quality.
- The Databricks job uses a demonstration bootstrap source and has no schedule.
- Model promotion, monitoring, retraining triggers, registry, serving, and production ingestion are
  outside the implemented repository scope.
- Cloud deployment and run state are external and can change independently of the repository.
