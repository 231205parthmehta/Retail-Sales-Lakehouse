from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"

def load_config() -> dict:
    #load project configuration from config.yaml.

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration File Not Found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open("r", encoding='utf-8') as file:
        config = yaml.safe_load(file)

    if not config:
        raise ValueError("Configuration File is Empty.")

    return config