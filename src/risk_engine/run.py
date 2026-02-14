from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import logging
import yaml

from risk_engine.analysis import run_analysis
from risk_engine.config import Config


def _setup_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("risk_engine")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


def run_pipeline(cfg: Config) -> Path:
    base_dir = Path(cfg.outputs_base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = base_dir / f"{ts}_{cfg.run_name}"
    run_dir.mkdir(parents=False, exist_ok=False)

    log_file = run_dir / "run.log"
    logger = _setup_logger(log_file)

    logger.info("Starting risk engine run")
    logger.info("Run directory: %s", run_dir)
    logger.info("Tickers: %s", cfg.tickers)
    logger.info("Date range: %s -> %s", cfg.start, cfg.end)

    if cfg.save_config_snapshot:
        snap = run_dir / "config_snapshot.yaml"
        with snap.open("w", encoding="utf-8") as f:
            yaml.safe_dump(cfg.raw, f, sort_keys=False)
        logger.info("Saved config snapshot: %s", snap.name)

    metrics = run_analysis(cfg, run_dir)
    logger.info("Saved metrics: %s", metrics)

    return run_dir
