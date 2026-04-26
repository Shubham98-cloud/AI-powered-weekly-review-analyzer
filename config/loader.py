import yaml
import os
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Optional
from pathlib import Path

class ProductConfig(BaseModel):
    name: str
    appstore_id: str
    playstore_id: str
    google_doc_id: str
    recipients: List[str]

class MCPServerConfig(BaseModel):
    command: List[str]

class ProductsYaml(BaseModel):
    products: List[ProductConfig]
    mcp_servers: Dict[str, MCPServerConfig]

class IngestionSettings(BaseModel):
    window_weeks: int
    max_reviews_per_product: int

class UMAPSettings(BaseModel):
    n_neighbors: int
    min_dist: float
    metric: str

class HDBSCANSettings(BaseModel):
    min_cluster_size: int
    min_samples: int

class LLMSettings(BaseModel):
    primary_model: str
    fallback_model: str
    max_output_tokens: int
    reviews_per_cluster: int

class NLPSettings(BaseModel):
    embedding_model: str
    umap: UMAPSettings
    hdbscan: HDBSCANSettings
    llm: LLMSettings
    quote_fuzzy_threshold: int

class MCPServerDeliveryConfig(BaseModel):
    enabled: bool
    mcp: MCPServerConfig

class DeliverySettings(BaseModel):
    google_docs: MCPServerDeliveryConfig
    gmail: MCPServerDeliveryConfig

class SettingsYaml(BaseModel):
    ingestion: IngestionSettings
    nlp: NLPSettings
    delivery: DeliverySettings

class ConfigError(Exception):
    pass

def load_yaml(file_path: Path) -> dict:
    if not file_path.exists():
        raise ConfigError(f"Config file not found: {file_path}")
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Error parsing YAML file {file_path}: {e}")

def load_config(config_dir: str = "config"):
    base_path = Path(config_dir)
    
    products_data = load_yaml(base_path / "products.yaml")
    settings_data = load_yaml(base_path / "settings.yaml")
    
    try:
        products_cfg = ProductsYaml(**products_data)
        settings_cfg = SettingsYaml(**settings_data)
        return products_cfg, settings_cfg
    except ValidationError as e:
        raise ConfigError(f"Configuration validation error: {e}")

if __name__ == "__main__":
    try:
        # For local testing, assume we are in the Phase1_Setup folder
        p, s = load_config()
        print(f"Loaded {len(p.products)} products.")
        print(f"Primary model: {s.nlp.llm.primary_model}")
    except Exception as e:
        print(f"Failed to load config: {e}")
