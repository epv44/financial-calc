import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_tabs(dfs: dict[str, pd.DataFrame], selected_range: tuple[pd.Timestamp, pd.Timestamp]) -> None:
    st.header("📉 Mortgage & Savings Information Over Time")

    loan_labels = list(dfs.keys())
    tab1, tab2, tab3, tab4, *loan_tabs = st.tabs([
        "Total Interest Paid",
        "Monthly Breakdown",
        "Net Worth",
        "Rent vs Own",
        *[f"{label} - Critical Metrics" for label in dfs.keys()]
    ])

    with tab1:
        st.subheader("Total Interest Paid Over Time (by Loan Type)")
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        for label, df in dfs.items():
            df_filtered = df[(df["ds"] >= selected_range[0])
                             & (df["ds"] <= selected_range[1])]
            ax1.plot(df_filtered["ds"],
                     df_filtered["total_interest_paid"], label=label)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Total Interest Paid ($)")
        ax1.set_title("Cumulative Interest Paid Over Time")
        ax1.legend()
        ax1.grid(True)
        st.pyplot(fig1)

    with tab2:
        st.subheader(
            "Monthly Breakdown: Interest vs. Principal (by Loan Type)")
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        for label, df in dfs.items():
            df_filtered = df[(df["ds"] >= selected_range[0])
                             & (df["ds"] <= selected_range[1])]
            ax2.plot(df_filtered["ds"], df_filtered["interest_payment"],
                     label=f"{label} - Interest", linestyle="--")
            ax2.plot(df_filtered["ds"], df_filtered["principle_paid"],
                     label=f"{label} - Principal", linestyle="-")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Monthly Payment ($)")
        ax2.set_title("Interest and Principal Components Over Time")
        ax2.legend(loc="upper right")
        ax2.grid(True)
        st.pyplot(fig2)

    with tab3:
        st.subheader("Net Worth: Buying vs Renting (by Loan Type)")
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        rent_plotted = False

        for label, df in dfs.items():
            df_filtered = df[(df["ds"] >= selected_range[0])
                             & (df["ds"] <= selected_range[1])]

            ax3.plot(
                df_filtered["ds"],
                df_filtered["net_worth_after_sale"],
                label=f"{label} - Buy"
            )

            if not rent_plotted:
                ax3.plot(
                    df_filtered["ds"],
                    df_filtered["net_worth_if_renting"],
                    label="Rent",
                    linestyle="--"
                )
                rent_plotted = True

            crossover = df_filtered[df_filtered["net_worth_after_sale"]
                                    >= df_filtered["net_worth_if_renting"]]
            if not crossover.empty:
                ax3.axvline(
                    x=crossover.iloc[0]["ds"],
                    color="gray",
                    linestyle="dotted",
                    alpha=0.5
                )

        ax3.set_xlabel("Date")
        ax3.set_ylabel("Net Worth ($)")
        ax3.set_title("Net Worth of Buying vs Renting")
        ax3.legend(loc="upper left")
        ax3.grid(True)
        st.pyplot(fig3)

    with tab4:
        st.subheader("Monthly Cost: Renting vs Owning (by Loan Type)")
        fig5, ax5 = plt.subplots(figsize=(12, 6))

        # Track whether we"ve already plotted rental
        rental_plotted = False

        for label, df in dfs.items():
            df_filtered = df[(df["ds"] >= selected_range[0])
                             & (df["ds"] <= selected_range[1])]

            ax5.plot(df_filtered["ds"], df_filtered["monthly_cost_ownership"],
                     label=f"{label} - Own", linestyle="-")

            # Only plot rental once
            if not rental_plotted:
                ax5.plot(df_filtered["ds"], df_filtered["rental_cost"],
                         label="Rent", linestyle="--")
                rental_plotted = True

        ax5.set_xlabel("Date")
        ax5.set_ylabel("Monthly Cost ($)")
        ax5.set_title("Monthly Rent Cost vs. Owning Cost")
        ax5.legend(loc="upper left")
        ax5.grid(True)
        st.pyplot(fig5)

        for loan_tab, label in zip(loan_tabs, loan_labels):
            with loan_tab:
                st.subheader(f"{label} - Critical Metrics")
                df = dfs[label]
                df_filtered = df[(df["ds"] >= selected_range[0])
                                 & (df["ds"] <= selected_range[1])]

                fig = go.Figure()

                for col in [
                    "cash_reserve",
                    "monthly_cost_ownership",
                    "principle_paid",
                    "interest_payment",
                    "loan_balance",
                    "net_profit_from_home_sale",
                    "net_worth_after_sale"
                ]:
                    fig.add_trace(go.Scatter(
                        x=df_filtered["ds"],
                        y=df_filtered[col],
                        mode="lines",
                        name=col.replace("_", " ").title(),
                        hovertemplate="%{x|%b %Y}<br>" +
                        f"{col.replace("_", " ").title()}: $%{{y:,.0f}}<extra></extra>"
                    ))

                fig.update_layout(
                    title=dict(
                        text=f"{label}: Simulation Critical Metrics Over Time",
                        font=dict(color="black", family="Arial"),
                        x=0.5,
                        xanchor="center"
                    ),
                    xaxis=dict(
                        title=dict(text="Date", font=dict(color="black")),
                        linecolor="black",
                        tickfont=dict(color="black"),
                        gridcolor="lightgray",
                        showline=True,
                        showgrid=True
                    ),
                    yaxis=dict(
                        title=dict(text="Amount ($)",
                                   font=dict(color="black")),
                        linecolor="black",
                        tickfont=dict(color="black"),
                        gridcolor="lightgray",
                        showline=True,
                        showgrid=True
                    ),
                    legend=dict(
                        x=0,
                        y=1,
                        bgcolor="rgba(255,255,255,0)",
                        font=dict(color="black", family="Arial"),
                        itemclick="toggle",
                        itemdoubleclick="toggleothers"
                    ),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(color="black", family="Arial")
                )

                st.plotly_chart(fig, use_container_width=True)
