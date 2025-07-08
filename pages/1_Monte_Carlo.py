
import numpy as np
import streamlit as st
from ui.monte_carlo.inputs import display_inputs
from ui.monte_carlo.outputs import display_output
from monte_carlo_sim import run_monte_carlo


st.set_page_config(page_title="Monte Carlo Simulation", layout="wide")
st.title("📈 Monte Carlo Simulation: Stock & Cash Portfolio")
st.markdown("Simulate different investment returns and appreciation scenarios.")


input = display_inputs()
output = run_monte_carlo(input)
display_output(output)
