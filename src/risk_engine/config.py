from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

@dataclass(frozen=True)
class Config:
    raw: Dict[str, Any]

    @property
    def run_name(self) -> str:
        return str(self.raw.get("run_name", "run"))
    
    @property
    def tickers(self) -> List[str]:
        uni = self.raw.get("universe", {}) or {}
        return list(uni.get("tickers", []))
    
    @property
    def start(self) -> str:
        dr = self.raw.get("date_range", {}) or {}
        v = dr.get("start")
        return "" if v is None else str(v)

    @property
    def end(self) -> str:
        dr = self.raw.get("date_range", {}) or {}
        v = dr.get("end")
        return "" if v is None else str(v)
    
    @property
    def outputs_base_dir(self) -> str:
        out = self.raw.get("outputs", {}) or {}
        return str(out.get("base_dir", "runs"))

    @property
    def save_config_snapshot(self) -> bool:
        out = self.raw.get("outputs", {}) or {}
        return bool(out.get("save_config_snapshot", True))
    
    @property
    def data_cache_dir(self) -> str:
        data = self.raw.get("data", {}) or {}
        return str(data.get("cache_dir", "data/cache"))
    
    @property
    def data_interval(self) -> str:
        data = self.raw.get("data", {}) or {}
        return str(data.get("interval", "1d"))

    @property
    def data_auto_adjust(self) -> bool:
        data = self.raw.get("data", {}) or {}
        return bool(data.get("auto_adjust", True))

    @property
    def data_force_refresh(self) -> bool:
        data = self.raw.get("data", {}) or {}
        return bool(data.get("force_refresh", False))
    
def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    tickers = (data.get("universe", {}) or {}).get("tickers", [])
    if not isinstance(tickers, list) or len(tickers) == 0:
        raise ValueError("Config must include universe.tickers as a non-empty list")

    dr = data.get("date_range", {}) or {}
    if not dr.get("start") or not dr.get("end"):
        raise ValueError("Config must include date_range.start and date_range.end (YYYY-MM-DD)")

    return Config(raw=data)