import pandas as pd
import streamlit as st

def classify_account(account_name):
    name = account_name.lower()
    if "revenue" in name or "income" in name:
        return "Revenue"
    elif ("expense" in name or "payroll" in name or "legal" in name or
          "cogs" in name or "cost of goods" in name or "fees" in name):
        return "Expense"
    else:
        return "Other"

def generate_pnl_report(df):
    asset_accounts = df[df['currencyId'].isna()]['accountName'].unique()
    digital_asset_account = asset_accounts[0] if len(asset_accounts) > 0 else None

    pnl_df = df[df['accountName'] != digital_asset_account]

    grouped = pnl_df.groupby("accountName").agg(
        total_debit=pd.NamedAgg(column="debit", aggfunc="sum"),
        total_credit=pd.NamedAgg(column="credit", aggfunc="sum")
    ).reset_index()

    grouped["account_type"] = grouped["accountName"].apply(classify_account)

    if digital_asset_account:
        asset_df = df[df["accountName"] == digital_asset_account]
        asset_summary = asset_df.groupby("accountName").agg(
            total_debit=pd.NamedAgg(column="debit", aggfunc="sum"),
            total_credit=pd.NamedAgg(column="credit", aggfunc="sum")
        ).reset_index()
        asset_summary["account_type"] = asset_summary["accountName"].apply(classify_account)

        digital_debit_total = asset_summary["total_debit"].values[0]
        digital_credit_total = asset_summary["total_credit"].values[0]
    else:
        asset_summary = pd.DataFrame(columns=["accountName", "total_debit", "total_credit", "account_type"])
        digital_debit_total = 0
        digital_credit_total = 0

    blank_rows = pd.DataFrame([{"accountName": "", "total_debit": "", "total_credit": "", "account_type": ""}] * 2)

    final_df = pd.concat([grouped, blank_rows, asset_summary], ignore_index=True)
    return final_df, digital_asset_account, digital_debit_total, digital_credit_total

st.set_page_config(page_title="P&L Report Generator", layout="wide")
st.title("P&L Statement from Bitwave Journal Entries")

uploaded_file = st.file_uploader("Upload Journal Entry CSV File", type=["csv"])

if uploaded_file:
    full_df = pd.read_csv(uploaded_file)

    full_df['localDateTime'] = pd.to_datetime(full_df['localDateTime'], errors='coerce')
    full_df['year'] = full_df['localDateTime'].dt.year
    full_df['month'] = full_df['localDateTime'].dt.month
    full_df['month_name'] = full_df['localDateTime'].dt.strftime('%B')
    full_df['quarter'] = full_df['localDateTime'].dt.to_period('Q').astype(str)

    tab_options = ['Monthly', 'Quarterly', 'Yearly']
    time_view = st.selectbox("Select Time Granularity for P&L", tab_options)

    if time_view == 'Monthly':
        for (year, month), group in full_df.groupby(['year', 'month']):
            tab_label = f"{pd.to_datetime(f'{year}-{month}-01').strftime('%B %Y')}"
            with st.expander(tab_label):
                pnl_df, digital_asset_account, digital_debit_total, digital_credit_total = generate_pnl_report(group)
                if digital_asset_account:
                    st.markdown(f"**Identified Digital Asset Account (for reconciliation):** `{digital_asset_account}`")
                    st.markdown(f"**Total Debits to Digital Asset Account:** `{digital_debit_total}`")
                    st.markdown(f"**Total Credits to Digital Asset Account:** `{digital_credit_total}`")
                else:
                    st.warning("No digital asset account identified. No entries with blank 'currencyId' found.")

                st.dataframe(pnl_df)

    elif time_view == 'Quarterly':
        for quarter, group in full_df.groupby('quarter'):
            with st.expander(f"Quarter: {quarter}"):
                pnl_df, digital_asset_account, digital_debit_total, digital_credit_total = generate_pnl_report(group)
                if digital_asset_account:
                    st.markdown(f"**Identified Digital Asset Account (for reconciliation):** `{digital_asset_account}`")
                    st.markdown(f"**Total Debits to Digital Asset Account:** `{digital_debit_total}`")
                    st.markdown(f"**Total Credits to Digital Asset Account:** `{digital_credit_total}`")
                else:
                    st.warning("No digital asset account identified. No entries with blank 'currencyId' found.")

                st.dataframe(pnl_df)

    elif time_view == 'Yearly':
        for year, group in full_df.groupby('year'):
            with st.expander(f"Year: {year}"):
                pnl_df, digital_asset_account, digital_debit_total, digital_credit_total = generate_pnl_report(group)
                if digital_asset_account:
                    st.markdown(f"**Identified Digital Asset Account (for reconciliation):** `{digital_asset_account}`")
                    st.markdown(f"**Total Debits to Digital Asset Account:** `{digital_debit_total}`")
                    st.markdown(f"**Total Credits to Digital Asset Account:** `{digital_credit_total}`")
                else:
                    st.warning("No digital asset account identified. No entries with blank 'currencyId' found.")

                st.dataframe(pnl_df)
