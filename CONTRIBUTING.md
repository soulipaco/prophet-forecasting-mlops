# Contributing

Thank you for improving the forecasting project. Keep changes small, evidence-led, and reversible.

## Development workflow

1. Create a focused branch from `main`.
2. Install the locked development environment with `uv sync --extra test`.
3. Preserve existing forecasting mathematics unless the old and new behaviors are both tested and the change is documented.
4. Run:

   ```bash
   uv run ruff check src tests scripts
   uv run ruff format --check src tests scripts
   uv run pytest
   uv build
   ```

5. Update `docs/traceability.md` when moving or changing notebook-derived behavior.
6. Open a pull request describing the evidence, behavioral impact, validation, and migration implications.

## Confidentiality rules

Never commit source notebooks, workbooks, real client records, credentials, workspace deployment state, anonymization mappings, or raw production outputs. Use neutral synthetic fixtures. Do not paste sensitive values into issues, logs, screenshots, test names, or exception snapshots.

If a confidentiality scan finds a potential residual, stop and report only the file and category—never print the matched value.

## Testing expectations

Add the smallest test that proves the behavior being changed. Depending on the change, this can include configuration validation, data contracts, transformation round trips, calendar splits, leakage prevention, metric calculations, forecast schemas, Prophet integration, or Databricks-marked integration tests.
