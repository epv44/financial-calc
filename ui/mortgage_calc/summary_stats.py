import pandas as pd
import streamlit as st


def display_summary_stats(dfs: dict[str, pd.DataFrame], selected_range: tuple[pd.Timestamp, pd.Timestamp]) -> None:
    st.header("📊 Summary Statistics by Loan Type")

    with st.expander("Summary Overview", expanded=True):
        cols = st.columns(len(dfs))  # one column per loan type

        for col, (label, df) in zip(cols, dfs.items()):
            df_filtered = df[(df['ds'] >= selected_range[0])
                             & (df['ds'] <= selected_range[1])]

            final_buy = df_filtered['net_worth_after_sale'].iloc[-1]
            final_rent = df_filtered['net_worth_if_renting'].iloc[-1]
            cash_negative_months = (df_filtered['cash_reserve'] < 0).sum()

            with col:
                st.markdown(f"### {label}")
                st.metric("Final Net Worth (Buy)", f"${final_buy:,.0f}")
                st.metric("Final Net Worth (Rent)", f"${final_rent:,.0f}")
                st.write(
                    f"📉 Negative Cash Reserve Months: **{cash_negative_months}**")

                st.dataframe(pd.DataFrame({
                    "Metric": [
                        "Min Cash Reserve",
                        "Max Cash Reserve",
                        "Avg Cash Reserve",
                        "Min Loan Balance",
                        "Avg Monthly Cost",
                        "Avg Profit from Sale"
                    ],
                    "Value": [
                        f"${df_filtered['cash_reserve'].min():,.0f}",
                        f"${df_filtered['cash_reserve'].max():,.0f}",
                        f"${df_filtered['cash_reserve'].mean():,.0f}",
                        f"${df_filtered['loan_balance'].min():,.0f}",
                        f"${df_filtered['monthly_cost_ownership'].mean():,.0f}",
                        f"${df_filtered['net_profit_from_home_sale'].mean():,.0f}"
                    ]
                }), use_container_width=True)
