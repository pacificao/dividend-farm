import streamlit as st
import pandas as pd
from dividend_bot import get_upcoming_dividends

# Streamlit page setup
st.set_page_config(page_title="Dividend Farming AI", layout="wide")
st.title("📈 Dividend Farming Assistant")
st.markdown("Select your preferences below to get recommended dividend stocks.")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Settings")
    min_yield = st.slider("Minimum Dividend Yield (%)", min_value=0.0, max_value=15.0, value=2.5, step=0.1)
    days_ahead = st.slider("Days Ahead to Scan", min_value=1, max_value=30, value=14)
    apply_filtering = st.checkbox("Hide OTC / Distressed / Untradable Tickers", value=True)

# Load data
with st.spinner("🔎 Analyzing upcoming dividends..."):
    df = get_upcoming_dividends(days_ahead=days_ahead, apply_filters=apply_filtering)

# Process and display results
if df.empty:
    st.warning("No qualifying dividend stocks found. Try adjusting your filters or check back later.")
else:
    df["Dividend Yield"] = pd.to_numeric(df["Dividend Yield"], errors="coerce")
    filtered_df = df[df["Dividend Yield"] >= min_yield]

    if filtered_df.empty:
        st.info("No stocks match your minimum dividend yield criteria.")
        with st.expander("📋 View all retrieved stocks anyway"):
            st.dataframe(df.reset_index(drop=True))
    else:
        st.success(f"✅ Found {len(filtered_df)} potential dividend picks:")
        st.dataframe(filtered_df.sort_values(by="Dividend Yield", ascending=False).reset_index(drop=True))