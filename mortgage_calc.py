from dataclasses import dataclass
from datetime import date
from dateutil.relativedelta import relativedelta
from enum import Enum
from mortgage_input import ARMRates, MortgageInput
from rental_sim import calculate_monthly_rental_cost
from typing import Tuple, List, Optional

import numpy_financial as npf
import pandas as pd


pd.set_option("float_format", "{:,}".format)


@dataclass
class MortgageData:
    principle_paid: float
    interest_payment: float
    projected_home_value: float
    net_profit_from_home_sale: float
    loan_balance: float
    cash_reserve: float
    # growth of net worth over time after home sale
    net_worth_after_sale: float
    # roi towards your net worth
    roi_net_worth: float
    # roi on the home purchase itself
    roi: float
    # money made after subtracting downpayment
    net_profit: float
    ds: date
    monthly_cost_ownership: float


class YearlyRateType(Enum):
    APY = 1
    APR = 2


# yearly interest rate per month
def ownership_costs(
    input: MortgageInput,
    periodic_interest_rate: float,
) -> Tuple[float, float, float]:
    """
    Returns: (monthly_operating_expenses, periodic_mortgage_payment, down_plus_closing)
    """
    payment_periods = input.loan_term * 12
    loan_amount = input.home_price - input.downpayment
    # https://www.nerdwallet.com/article/mortgages/closing-costs-mortgage-fees-explained
    closing_costs = loan_amount * input.closing_cost_percentage
    down_plus_closing = input.downpayment + closing_costs
    if input.should_add_closing_to_loan:
        mortgage = (input.home_price + closing_costs) - input.downpayment
    else:
        mortgage = input.home_price - input.downpayment

    periodic_mortgage_payment = -1*npf.pmt(
        periodic_interest_rate, payment_periods, mortgage
    )

    monthly_property_tax = input.home_price * (input.property_tax_rate/12)

    monthly_operating_expenses = (
        input.monthly_pmi
        + input.monthly_hoa
        + input.monthly_insurance
        + input.monthly_maintenance_fund
        + periodic_mortgage_payment
        + monthly_property_tax
    )

    return float(monthly_operating_expenses), float(periodic_mortgage_payment), down_plus_closing


def adjust_arm_payment(
    row: int,
    loan_balance: float,
    months_remaining: int,
    current_rate: float,
    periodic_interest_rate: float,
    arm_input: ARMRates,
    last_rate_adjustment_month: int,
) -> tuple[float, float, int]:
    """
    Returns: (new_rate, new_payment, new_last_rate_adjustment_month)
    """
    max_rate = periodic_interest_rate + arm_input.monthly_lifetime_cap
    months_since_adjustment = row - arm_input.fixed_period_months
    cap = 0
    if months_since_adjustment == 0:
        cap = arm_input.monthly_initial_cap
    elif (row - last_rate_adjustment_month) >= 12:
        cap = arm_input.monthly_annual_cap

    if cap > 0 and months_remaining > 0:
        last_rate_adjustment_month = row
        current_rate = min(current_rate + cap, max_rate)
        new_payment = float(-1 * npf.pmt(current_rate,
                            months_remaining, loan_balance))
    else:
        new_payment = float(-1 * npf.pmt(current_rate,
                            months_remaining, loan_balance))

    return current_rate, new_payment, last_rate_adjustment_month


def calculate_monthly_cost_and_loan_balance(
    monthly_operating_expenses: float,
    down_plus_closing: float,
    periodic_mortgage_payment: float,
    input: MortgageInput,
    periodic_interest_rate: float,
    simulation_length_months: int,
    rental_money: float = 0.0,
    starting_loan_balance: Optional[float] = None,
) -> List[MortgageData]:
    total_term_months = input.loan_term * 12
    loan_balance = starting_loan_balance if starting_loan_balance is not None else input.home_price - input.downpayment
    projected_home_value = input.home_price
    data = []

    cash_reserve = input.starting_cash - down_plus_closing

    current_rate = periodic_interest_rate
    current_payment = periodic_mortgage_payment
    last_rate_adjustment_month = -1
    for row in range(simulation_length_months):
        months_remaining = total_term_months - row

        if input.is_arm and input.arm_rates and row >= input.arm_rates.fixed_period_months:
            current_rate, current_payment, last_rate_adjustment_month = adjust_arm_payment(
                row,
                loan_balance,
                months_remaining,
                current_rate,
                periodic_interest_rate,
                input.arm_rates,
                last_rate_adjustment_month,
            )

            monthly_property_tax = input.home_price * \
                (input.property_tax_rate / 12)
            monthly_operating_expenses = (
                input.monthly_pmi
                + input.monthly_hoa
                + input.monthly_insurance
                + input.monthly_maintenance_fund
                + current_payment
                + monthly_property_tax
            )

        # Determine monthly payment breakdown
        if row < total_term_months:
            interest_payment = loan_balance * current_rate
            principal_paid = current_payment - interest_payment
        else:
            principal_paid = 0
            interest_payment = 0
            monthly_operating_expenses = (
                input.monthly_pmi
                + input.monthly_hoa
                + input.monthly_insurance
                + input.monthly_maintenance_fund
                + (input.home_price * input.property_tax_rate / 12)
            )

        ds = input.purchase_date + relativedelta(months=row + 1)
        projected_home_value = input.home_price * \
            (1 + input.property_appreciation) ** (row / 12)

        # Capital gains logic
        gross_gain = projected_home_value - input.home_price - \
            projected_home_value * input.realtor_fee_at_sale
        if gross_gain > 0:
            capital_gains = gross_gain * input.capital_gains_tax
            net_profit_at_sale = (
                projected_home_value *
                (1 - input.realtor_fee_at_sale) - loan_balance - capital_gains
            )
        else:
            net_profit_at_sale = projected_home_value * \
                (1 - input.realtor_fee_at_sale) - loan_balance

        net_worth_after_sale = net_profit_at_sale + cash_reserve
        net_profit = net_profit_at_sale
        roi = net_profit / down_plus_closing
        roi_net_worth = (net_profit + cash_reserve) / down_plus_closing
        monthly_income = input.monthly_income * \
            (1 + input.yearly_increase) ** (row / 12)
        monthly_savings = monthly_income - monthly_operating_expenses
        cash_reserve = (
            cash_reserve * (1 + input.stock_interest_rate / 12)
            + monthly_savings
            + rental_money
            - monthly_operating_expenses
        )

        loan_balance -= principal_paid

        data.append(MortgageData(
            round(principal_paid, 2),
            round(interest_payment, 2),
            round(projected_home_value, 2),
            round(net_profit_at_sale, 2),
            round(loan_balance, 2),
            round(cash_reserve, 2),
            round(net_worth_after_sale, 2),
            roi_net_worth,
            roi,
            round(net_profit, 2),
            ds,
            round(monthly_operating_expenses, 2),
        ))

    return data


def periodic_interest_rate(mortgage_interest_rate: float, interest_rate_type: YearlyRateType) -> float:
    return (mortgage_interest_rate / 12
            if interest_rate_type == YearlyRateType.APY
            else ((1 + mortgage_interest_rate) ** (1 / 12) - 1)
            )


def run_mortgage_calc(input: MortgageInput) -> pd.DataFrame:
    pir = periodic_interest_rate(
        mortgage_interest_rate=input.mortgage_interest_rate, interest_rate_type=YearlyRateType.APR)

    monthly_operating_expenses, monthly_mortgage, down_plus_closing = ownership_costs(
        input=input,
        periodic_interest_rate=pir,
    )

    mortgage_data = calculate_monthly_cost_and_loan_balance(
        monthly_operating_expenses=monthly_operating_expenses,
        down_plus_closing=down_plus_closing,
        periodic_mortgage_payment=monthly_mortgage,
        input=input,
        periodic_interest_rate=pir,
        simulation_length_months=30*12,
    )

    df_rent = calculate_monthly_rental_cost(
        simulation_length_months=30*12, input=input)

    df_own = pd.DataFrame([vars(s) for s in mortgage_data])
    df_own["total_interest_paid"] = df_own["interest_payment"].cumsum()
    df = pd.merge(df_own, df_rent, on="ds", how="left")

    return df


def run_mortgage_simulation(
    home_price: float,
    downpayment: float,
    loan_options: dict[str, dict[str, str]],
    property_appreciation: float,
    starting_cash: float,
    realtor_fee_at_sale: float,
    capital_gains_tax: float,
    monthly_rent: float,
    rental_increase_pct: float,
    stock_interest_rate: float,
    monthly_income_saved: float,
    yearly_increase: float,
    closing_cost_percentage: float,
    property_tax_rate: float,
    should_add_closing_to_loan: bool,
    monthly_pmi: float,
    monthly_hoa: float,
    monthly_insurance: float,
    monthly_maintenance_fund: float,
) -> dict[str, pd.DataFrame]:
    dfs = {}
    for label, opt in loan_options.items():
        is_arm = (label == "5/1 ARM")
        input = MortgageInput(
            home_price=home_price,
            downpayment=downpayment,
            mortgage_interest_rate=float(opt["rate"]),
            loan_term=int(opt["term"]),
            property_appreciation=property_appreciation,
            starting_cash=starting_cash,
            realtor_fee_at_sale=realtor_fee_at_sale,
            capital_gains_tax=capital_gains_tax,
            monthly_rent=monthly_rent,
            rental_increase_pct=rental_increase_pct,
            stock_interest_rate=stock_interest_rate,
            monthly_income=monthly_income_saved,
            yearly_increase=yearly_increase,
            closing_cost_percentage=closing_cost_percentage,
            property_tax_rate=property_tax_rate,
            should_add_closing_to_loan=should_add_closing_to_loan,
            monthly_pmi=monthly_pmi,
            monthly_hoa=monthly_hoa,
            monthly_insurance=monthly_insurance,
            monthly_maintenance_fund=monthly_maintenance_fund,
            arm_rates=ARMRates() if is_arm else None,
            is_arm=is_arm,
        )
        df_option = run_mortgage_calc(input)
        dfs[label] = df_option

    return dfs
