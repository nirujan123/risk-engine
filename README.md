# Risk Engine

A modular Python risk engine for portfolio analysis.

This project computes core portfolio risk metrics using historical market data:

- Volatility (daily and annualised)
- Maximum Drawdown
- Historical Value at Risk (VaR)
- Historical Expected Shortfall (ES)
- Parametric (Normal) VaR

The engine is designed with clean separation of concerns:
- Data layer
- Risk mathematics layer
- Analysis layer
- Reporting layer
- CLI interface

---

## Installation & Usage

```bash
git clone <your-repo-url>
cd risk-engine

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
# source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the engine
python -m risk_engine run --config configs/demo.yaml
```

