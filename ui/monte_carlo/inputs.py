import streamlit as st
from monte_carlo_sim import MonteCarloInput


def display_inputs() -> MonteCarloInput:
    years = st.slider("Years", 5, 30, 30)
    n_simulations = st.slider("Number of Simulations", 100, 5000, 1000)

    st.markdown("### 💰 Starting Balances")
    stock_start = st.number_input(
        "Starting Stock Balance ($)", value=600_000.0)
    cash_start = st.number_input("Starting Cash Balance ($)", value=600_000.0)

    st.markdown("### ➕ Monthly Contributions")
    monthly_stock_contribution = st.number_input(
        "Monthly Stock Contribution ($)", value=0.0, step=100.0)
    monthly_cash_contribution = st.number_input(
        "Monthly Cash Contribution ($)", value=0.0, step=100.0)

    st.markdown("### 🏠 Home Purchase Withdrawal")
    withdraw_year = st.slider("Withdrawal Year", 0, years, 5)

    withdraw_stock = st.number_input(
        "Withdraw from Stock ($)", value=200_000.0, min_value=0.0, max_value=stock_start)
    withdraw_cash = st.number_input(
        "Withdraw from Cash ($)", value=100_000.0, min_value=0.0, max_value=cash_start)

    st.markdown("### 📈 Stock Return Assumptions")
    stock_mean = st.slider("Stock Annual Return (%)", 0.0, 12.0, 6.5) / 100
    stock_vol = st.slider("Stock Annual Volatility (%)", 0.0, 50.0, 18.0) / 100

    st.markdown("### 💵 Cash Return Assumptions")
    cash_mean = st.slider("Cash Annual Return (%)", 0.0, 6.0, 3.0) / 100
    cash_vol = st.slider("Cash Annual Volatility (%)", 0.0, 5.0, 0.5) / 100

    return MonteCarloInput(
        years=years,
        n_simulations=n_simulations,
        stock_start=stock_start,
        cash_start=cash_start,
        withdraw_year=withdraw_year,
        withdraw_stock=withdraw_stock,
        withdraw_cash=withdraw_cash,
        stock_mean=stock_mean,
        stock_vol=stock_vol,
        cash_mean=cash_mean,
        cash_vol=cash_vol,
        monthly_stock_contribution=monthly_stock_contribution,  # NEW
        monthly_cash_contribution=monthly_cash_contribution     # NEW
    )
