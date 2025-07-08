## Financial Calc

A flexible Monte Carlo simulation and rent-vs-buy analysis tool for personal finance decisions. Built with Python and Streamlit.

## Features

- Monte Carlo Simulator for projecting investment outcomes with:
  - Customizable stock/cash returns, volatilities, and withdrawal plans
  - Monthly contributions and time-based withdrawals
- Rent vs Buy Calculator for home affordability modeling:
  - Adjustable rate mortgage (ARM) logic with caps
  - Monthly income, rent, ownership cost modeling
  - Tracks long-term net worth in both scenarios

## Demo

Launch the app locally:

```bash
python3 -m streamlit run Rent_vs_Buy.py
```

## Setup
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt