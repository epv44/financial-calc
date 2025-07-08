import streamlit as st

import pandas as pd
from ui.mortgage_calc.form import run_simulation_if_submitted, render_form
from ui.app_session import init_form_defaults, update_arm_toggle
from ui.mortgage_calc.tabs import render_tabs
from ui.mortgage_calc.summary_stats import display_summary_stats


def validate_simulation(dfs: dict[str, pd.DataFrame]) -> None:
    for label, df in dfs.items():
        if (df['cash_reserve'] < 0).any():
            st.error(
                f"⚠️ In **{label}**, cash reserve went negative. Consider increasing income or reducing the loan.")


st.set_page_config(
    page_title="Financial Planner",
    page_icon="📈",
    layout="wide"
)

st.title("Welcome to the most straightforward financial calculator")
init_form_defaults()
st.radio(
    "Include an ARM Loan?",
    ["No", "Yes"],
    index=1 if st.session_state.use_arm == "Yes" else 0,
    key="use_arm_radio",
    on_change=lambda: update_arm_toggle()
)

# Run main form and gather inputs
submitted = render_form()

# Trigger simulation and show results
dfs = run_simulation_if_submitted(submitted)

# Show tabs with results
if dfs:
    all_dates = pd.concat([df['ds'] for df in dfs.values()])
    min_date = all_dates.min()
    max_date = all_dates.max()

    selected_range = st.slider(
        "Select date range to display on plots:",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MM/YYYY"
    )
    validate_simulation(dfs)
    display_summary_stats(dfs, selected_range)
    render_tabs(dfs, selected_range)
