from mortgage_calc import run_mortgage_simulation
import pandas as pd
import streamlit as st


def render_form() -> bool:
    with st.form("mortgage_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🏠 Home Purchase Info")
            st.number_input("Home Price ($)", key="home_price", step=10_000.0)
            st.number_input("Downpayment ($)",
                            key="downpayment", step=10_000.0)
            st.number_input(
                "Monthly Income ($)",
                key="monthly_income_saved",
                step=100.0,
                help="After tax income minus expenses, but including rent or mortgage payment (if not used for rent this money would be saved)",
            )
            st.number_input(
                "Monthly HOA ($)",
                key="monthly_hoa",
                step=100.0,
                help="Can be zero if your property does not have an HOA",
            )
            st.number_input(
                "Monthly Home Maintenance Fund",
                key="monthly_maintenance_fund",
                step=100.0,
                help="Amount saved each month for home maintence, the expectation is this is used to cover home related costs",
            )
            st.number_input(
                "Monthly Home Insurance",
                key="monthly_insurance",
                step=100.0,
                help="Homeowners insurance as if paid monthly",
            )
            st.subheader("💸 Taxes and Loan Cost")
            st.number_input(
                "Closing Cost (%)", key="closing_cost_percentage", step=0.1, format="%.2f")
            st.number_input("Property Tax (%)",
                            key="property_tax_rate", step=0.1, format="%.2f")
            st.number_input(
                "Realtor Fee (%)", key="realtor_fee_at_sale", step=0.1, format="%.2f") / 100
            st.number_input(
                "Capital Gains Tax (%)", key="capital_gains_tax", step=1.0, format="%.0f") / 100

            st.checkbox("Roll Closing Costs into Loan?",
                        key="should_add_closing_to_loan")

        with col2:
            st.subheader("💰 Mortgage Rates")
            st.number_input("30-Year Fixed Rate (%)",
                            key="rate_30", step=0.1, format="%.2f")
            st.number_input("15-Year Fixed Rate (%)",
                            key="rate_15", step=0.1, format="%.2f")
            if st.session_state.use_arm == "Yes":
                st.subheader("🏦 ARM Loan Data")
                st.number_input("5/1 ARM Rate (%)", key="rate_arm",
                                step=0.1, format="%.2f")
                st.number_input("ARM Fixed Period (years)",
                                key="arm_fixed_period", step=1)
                st.number_input("Initial ARM Adjustment Cap (%)",
                                key="arm_initial_cap", step=0.1, format="%.1f")
                st.number_input("Annual ARM Cap (%)",
                                key="arm_annual_cap", step=0.1, format="%.1f")
                st.number_input("Lifetime ARM Cap (%)",
                                key="arm_lifetime_cap", step=0.1, format="%.1f")

        with col3:
            st.subheader("📈 Market & Investment")
            st.number_input(
                "Home Appreciation (%)", key="property_appreciation", step=0.1, format="%.2f") / 100
            st.number_input(
                "Savings($)",
                key="starting_cash",
                step=10_000.0,
                help="Your savings that would be used for downpayment and are assumed to be majority stock",
            )
            st.number_input(
                "Stock Return (%)", key="stock_interest_rate", step=0.1, format="%.2f") / 100
            st.number_input(
                "Savings Growth (%)",
                key="yearly_increase",
                step=0.1,
                format="%.2f",
                help="Percentage change you will save each subsequent year, this could increase each year due to salary increase",
            ) / 100
            st.subheader("🏠 Rental Information")
            st.number_input(
                "Monthly Rent ($)", key="monthly_rent", step=250.0)
            st.number_input(
                "Yearly Rent Increase (%)",
                key="rental_increase_pct",
                step=0.1,
                format="%.2f",
                help="Percentage your rent is likely to increase by each year",
            ) / 100
            st.markdown("###")

        v = st.form_submit_button("Submit")
        return v


def run_simulation_if_submitted(submitted: bool) -> dict[str, pd.DataFrame]:
    """Run the simulation if the form was submitted."""
    if not submitted:
        return st.session_state.get("dfs")

    def pct(key): return st.session_state[key] / 100

    loan_options = {
        "30-year fixed": {
            "term": 30,
            "rate": pct("rate_30"),
        },
        "15-year fixed": {
            "term": 15,
            "rate": pct("rate_15"),
        }
    }

    if st.session_state.use_arm == "Yes":
        loan_options["5/1 ARM"] = {
            "term": 30,
            "rate": pct("rate_arm"),
            "arm_fixed_period": st.session_state.arm_fixed_period,
            "arm_initial_cap": pct("arm_initial_cap"),
            "arm_annual_cap": pct("arm_annual_cap"),
            "arm_lifetime_cap": pct("arm_lifetime_cap"),
        }

    dfs = run_mortgage_simulation(
        home_price=st.session_state.home_price,
        downpayment=st.session_state.downpayment,
        loan_options=loan_options,
        property_appreciation=pct("property_appreciation"),
        starting_cash=st.session_state.starting_cash,
        realtor_fee_at_sale=pct("realtor_fee_at_sale"),
        capital_gains_tax=pct("capital_gains_tax"),
        monthly_rent=st.session_state.monthly_rent,
        rental_increase_pct=pct("rental_increase_pct"),
        stock_interest_rate=pct("stock_interest_rate"),
        monthly_income_saved=st.session_state.monthly_income_saved,
        yearly_increase=pct("yearly_increase"),
        closing_cost_percentage=pct("closing_cost_percentage"),
        property_tax_rate=pct("property_tax_rate"),
        should_add_closing_to_loan=st.session_state.should_add_closing_to_loan,
        monthly_pmi=st.session_state.monthly_pmi,
        monthly_hoa=st.session_state.monthly_hoa,
        monthly_insurance=st.session_state.monthly_insurance,
        monthly_maintenance_fund=st.session_state.monthly_maintenance_fund,
    )

    st.session_state["dfs"] = dfs
    return dfs
