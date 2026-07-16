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

5. Update the architecture decision records when changing system behavior or operational contracts.
6. Open a pull request describing the evidence, behavioral impact, validation, and migration implications.

## Repository hygiene

Never commit credentials, local environment files, workspace deployment state, or raw production outputs. Use deterministic synthetic fixtures in tests and demonstrations. Keep logs, screenshots, test names, and exception snapshots free of customer data.

## Testing expectations

Add the smallest test that proves the behavior being changed. Depending on the change, this can include configuration validation, data contracts, transformation round trips, calendar splits, leakage prevention, metric calculations, forecast schemas, Prophet integration, or Databricks-marked integration tests.
