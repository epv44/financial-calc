from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class ARMRates:
    fixed_period: int = 5
    # 2% max jump at first adjustment
    initial_arm_cap: float = 0.02
    # 1% per year after that
    annual_arm_cap: float = 0.01
    # 5% total max increase
    lifetime_arm_cap: float = 0.05

    @property
    def monthly_annual_cap(self) -> float:
        return self.annual_arm_cap / 12

    @property
    def monthly_initial_cap(self) -> float:
        return self.initial_arm_cap / 12

    @property
    def monthly_lifetime_cap(self) -> float:
        return self.lifetime_arm_cap / 12

    @property
    def fixed_period_months(self) -> int:
        return self.fixed_period * 12


@dataclass
class MortgageInput:
    home_price: float
    downpayment: float
    mortgage_interest_rate: float
    loan_term: int
    property_appreciation: float
    starting_cash: float
    realtor_fee_at_sale: float
    capital_gains_tax: float
    monthly_rent: float
    rental_increase_pct: float
    stock_interest_rate: float
    monthly_income: float
    yearly_increase: float
    closing_cost_percentage: float
    property_tax_rate: float
    should_add_closing_to_loan: bool
    monthly_pmi: float
    monthly_hoa: float
    monthly_insurance: float
    monthly_maintenance_fund: float
    arm_rates: Optional[ARMRates]
    is_arm: bool = False
    purchase_date: date = date.today()
