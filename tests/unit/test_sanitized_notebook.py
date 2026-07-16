import json
from pathlib import Path


def test_sanitized_notebook_has_no_persisted_state() -> None:
    notebook = json.loads(Path("sanitized_source/forecasting_pipeline_anonymized.ipynb").read_text(encoding="utf-8"))
    assert all(not cell.get("outputs") for cell in notebook["cells"])
    assert all(cell.get("execution_count") is None for cell in notebook["cells"] if cell.get("cell_type") == "code")
    assert all(not cell.get("metadata") for cell in notebook["cells"])
