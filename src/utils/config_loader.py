import yaml
import os
from typing import Dict, Any


def load_table_config() -> Dict[str, Any]:
    """
    Load the entire table_mapping.yaml and return the 'tables' section.

    Expected YAML format:

    tables:
      Guarantee:
        sf: "data/raw/guarantee_sf.csv"
        laweb: "data/raw/guarantee_laweb.csv"
        primary_key: "ID"
        dtype_map: null
      StoricoReferenteEntita:
        sf: "data/raw/StoricoReferenteEntita_SF.csv"
        laweb: "data/raw/StoricoReferenteEntita_LAWEB.csv"
        primary_key: "ID"
        dtype_map: null
    """
    config_path = os.path.join("config", "table_mapping.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"YAML configuration not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if "tables" not in data:
        raise ValueError("YAML file must contain a top-level 'tables:' section.")

    return data["tables"]
