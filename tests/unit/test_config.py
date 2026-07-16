from pathlib import Path

import pytest

from forecasting_project.config import ProjectConfig

ROOT = Path(__file__).parents[2]


def test_loads_dev_overlay() -> None:
    config = ProjectConfig.from_yaml(ROOT / "conf/base.yml", ROOT / "conf/dev.yml")
    assert config.environment == "dev"
    assert config.storage.catalog == "mlops_dev"
    assert config.storage.schema_name == "forecasting_project"
    assert config.tuning.trials == 2


def test_targets_cannot_be_regressors() -> None:
    config = ProjectConfig.from_yaml(ROOT / "conf/base.yml")
    payload = config.model_dump()
    payload["regressor_columns"] = [config.volume_column]
    with pytest.raises(ValueError, match="targets cannot also be regressors"):
        ProjectConfig.model_validate(payload)
