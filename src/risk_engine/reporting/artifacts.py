from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_series_csv(path: Path, s: pd.Series, name: str) -> None:
    df = s.to_frame(name=name)
    df.to_csv(path, index=True)


def save_metrics_json(path: Path, metrics: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def plot_drawdown(path: Path, drawdown: pd.Series) -> None:
    plt.figure()
    drawdown.plot()
    plt.title("Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
