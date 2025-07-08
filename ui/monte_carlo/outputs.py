import streamlit as st
from monte_carlo_sim import MonteCarloOutput
import matplotlib.pyplot as plt
import numpy as np


def display_output(output: MonteCarloOutput) -> None:
    input = output.input

    st.markdown("### 📊 Simulated Net Worth Over Time")

    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(min(100, input.n_simulations)):
        ax.plot(output.total_paths[i], alpha=0.1, linewidth=0.8)

    ax.plot(output.median_path, color='black', label="Median", linewidth=2)

    ax.axvline(
        input.withdraw_month,
        linestyle='dashed',
        color='red',
        label=f"Home Purchase (Year {input.withdraw_year})"
    )

    ax.set_xticks(np.arange(0, input.n_months + 1, 12))
    ax.set_xticklabels([str(i) for i in range(0, input.years + 1)])
    ax.set_xlabel("Years")
    ax.set_ylabel("Total Portfolio Value ($)")
    ax.set_title("Simulated Net Worth After Timed Withdrawal")
    ax.legend()

    st.pyplot(fig)

    st.markdown("### 📈 Final Portfolio Value Statistics")
    st.write(f"Median: ${np.median(output.final_values):,.0f}")
    st.write(
        f"10th Percentile: ${np.percentile(output.final_values, 10):,.0f}")
    st.write(
        f"90th Percentile: ${np.percentile(output.final_values, 90):,.0f}")

    st.markdown("### 🏡 Home Purchase")
    st.write(f"Withdraw Year: {input.withdraw_year}")
    st.write(
        f"Total Withdrawn: ${input.withdraw_stock + input.withdraw_cash:,.0f}")
