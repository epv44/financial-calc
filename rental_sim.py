from dataclasses import dataclass
from datetime import date
from dateutil.relativedelta import relativedelta
from mortgage_input import MortgageInput

import pandas as pd


@dataclass
class RentalData:
    ds: date
    rental_cost: float
    net_worth_if_renting: float


def calculate_monthly_rental_cost(simulation_length_months: int, input: MortgageInput) -> pd.DataFrame:
    rental_cost_monthly = input.monthly_rent
    cash_reserve_rental = input.starting_cash
    data = []
    for row in range(simulation_length_months):
        ds = input.purchase_date + relativedelta(months=row + 1)
        # Rent path updates
        if row % 12 == 0:
            rental_cost_monthly *= (1 + input.rental_increase_pct)

        monthly_income = input.monthly_income * \
            (1 + input.yearly_increase) ** (row / 12)
        monthly_savings = monthly_income - rental_cost_monthly

        cash_reserve_rental = (
            cash_reserve_rental * (1 + input.stock_interest_rate / 12)
            + monthly_savings
        )
        data.append(
            RentalData(
                ds=ds,
                rental_cost=round(rental_cost_monthly, 2),
                net_worth_if_renting=round(cash_reserve_rental, 2),
            )
        )

    return pd.DataFrame([vars(s) for s in data])
