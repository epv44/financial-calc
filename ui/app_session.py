import streamlit as st


def init_form_defaults() -> None:
    """Initialize all input defaults once per session."""
    defaults = {
        "home_price": 1_250_000.0,
        "downpayment": 800_000.0,
        "closing_cost_percentage": 2.5,
        "property_tax_rate": 1.1,
        "should_add_closing_to_loan": False,
        "rate_30": 6.5,
        "rate_15": 5.75,
        "rate_arm": 5.25,
        "monthly_pmi": 0.0,
        "monthly_hoa": 0.0,
        "monthly_insurance": 490.0,
        "monthly_maintenance_fund": 200.0,
        "property_appreciation": 2.0,
        "starting_cash": 1_200_000.0,
        "stock_interest_rate": 6.0,
        "monthly_rent": 6000.0,
        "rental_increase_pct": 1.7,
        "monthly_income_saved": 6_500.0,
        "yearly_increase": 2.5,
        "realtor_fee_at_sale": 6.0,
        "capital_gains_tax": 30.0,
        "use_arm": "Yes",
        "arm_fixed_period": 5,
        "arm_initial_cap": 2.0,
        "arm_annual_cap": 2.0,
        "arm_lifetime_cap": 5.0,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def update_arm_toggle() -> None:
    """Update the ARM toggle value and trigger UI refresh."""
    st.session_state.use_arm = st.session_state.use_arm_radio
