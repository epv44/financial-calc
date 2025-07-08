from dataclasses import dataclass
import numpy as np


@dataclass
class MonteCarloInput:
    years: int
    n_simulations: int
    stock_start: float
    cash_start: float
    withdraw_year: int
    withdraw_stock: float
    withdraw_cash: float
    stock_mean: float
    stock_vol: float
    cash_mean: float
    cash_vol: float
    monthly_stock_contribution: float
    monthly_cash_contribution: float

    @property
    def n_months(self) -> int:
        return self.years * 12

    @property
    def withdraw_month(self) -> int:
        return self.withdraw_year * 12


@dataclass
class MonteCarloOutput:
    # shape: (n_simulations, n_months)
    total_paths: np.ndarray
    stock_paths: np.ndarray
    cash_paths: np.ndarray
    median_path: np.ndarray
    final_values: np.ndarray
    input: "MonteCarloInput"


def run_monte_carlo(input: MonteCarloInput) -> MonteCarloOutput:
    np.random.seed(42)

    # Pre-withdrawal period
    stock_returns_pre = 1 + np.random.normal(input.stock_mean / 12, input.stock_vol / np.sqrt(12),
                                             (input.n_simulations, input.withdraw_month))
    cash_returns_pre = 1 + np.random.normal(input.cash_mean / 12, input.cash_vol / np.sqrt(12),
                                            (input.n_simulations, input.withdraw_month))

    stock_growth_pre = np.zeros_like(stock_returns_pre)
    cash_growth_pre = np.zeros_like(cash_returns_pre)

    stock_growth_pre[:, 0] = input.stock_start * \
        stock_returns_pre[:, 0] + input.monthly_stock_contribution
    cash_growth_pre[:, 0] = input.cash_start * \
        cash_returns_pre[:, 0] + input.monthly_cash_contribution

    for month in range(1, input.withdraw_month):
        stock_growth_pre[:, month] = (
            stock_growth_pre[:, month - 1] + input.monthly_stock_contribution) * stock_returns_pre[:, month]
        cash_growth_pre[:, month] = (
            cash_growth_pre[:, month - 1] + input.monthly_cash_contribution) * cash_returns_pre[:, month]

    # Withdrawal
    if input.withdraw_month > 0:
        stock_at_withdraw = stock_growth_pre[:, -1]
        cash_at_withdraw = cash_growth_pre[:, -1]
    else:
        stock_at_withdraw = np.full(input.n_simulations, input.stock_start)
        cash_at_withdraw = np.full(input.n_simulations, input.cash_start)

    stock_after = np.maximum(0, stock_at_withdraw - input.withdraw_stock)
    cash_after = np.maximum(0, cash_at_withdraw - input.withdraw_cash)

    months_remaining = input.n_months - input.withdraw_month

    # Post-withdrawal period
    stock_returns_post = 1 + np.random.normal(input.stock_mean / 12, input.stock_vol / np.sqrt(12),
                                              (input.n_simulations, months_remaining))
    cash_returns_post = 1 + np.random.normal(input.cash_mean / 12, input.cash_vol / np.sqrt(12),
                                             (input.n_simulations, months_remaining))

    stock_growth_post = np.zeros_like(stock_returns_post)
    cash_growth_post = np.zeros_like(cash_returns_post)

    if months_remaining > 0:
        stock_growth_post[:, 0] = stock_after * \
            stock_returns_post[:, 0] + input.monthly_stock_contribution
        cash_growth_post[:, 0] = cash_after * \
            cash_returns_post[:, 0] + input.monthly_cash_contribution

        for month in range(1, months_remaining):
            stock_growth_post[:, month] = (
                stock_growth_post[:, month - 1] + input.monthly_stock_contribution) * stock_returns_post[:, month]
            cash_growth_post[:, month] = (
                cash_growth_post[:, month - 1] + input.monthly_cash_contribution) * cash_returns_post[:, month]

    # Combine results
    if input.withdraw_month > 0:
        stock_paths = np.concatenate(
            [stock_growth_pre, stock_growth_post], axis=1)
        cash_paths = np.concatenate(
            [cash_growth_pre, cash_growth_post], axis=1)
    else:
        stock_paths = stock_growth_post
        cash_paths = cash_growth_post

    total_paths = stock_paths + cash_paths
    median_path = np.median(total_paths, axis=0)
    final_values = total_paths[:, -1]

    return MonteCarloOutput(
        total_paths=total_paths,
        stock_paths=stock_paths,
        cash_paths=cash_paths,
        median_path=median_path,
        final_values=final_values,
        input=input,
    )
