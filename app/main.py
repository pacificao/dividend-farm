import streamlit as st
import pandas as pd
from core.screener import get_upcoming_dividends
from core.filters import apply_filters
from db.queries import load_filtered_dividends

# --------------------------------------
# Streamlit App Configuration
# --------------------------------------
st.set_page_config(page_title="Dividend Farming AI", layout="wide")
st.title("📈 Dividend Farming Assistant")
st.markdown("Fine-tune your settings below to uncover dividend-paying stock opportunities.")

# --------------------------------------
# Sidebar: Filter Settings
# --------------------------------------
with st.sidebar:
    st.header("🔍 Filter Settings")
    data_source = st.radio("Data Source", ["Live API", "PostgreSQL Cache"], index=0)
    min_yield = st.slider("Minimum Dividend Yield (%)", 0.0, 15.0, 2.5, 0.1)
    days_ahead = st.slider("Days Ahead to Scan", 1, 30, 14)

    st.divider()
    st.markdown("**Optional Filters**")
    strict_filtering = st.checkbox("Hide OTC / Distressed / Untradable Tickers", value=True)
    exclude_f = st.checkbox("Exclude .F (Foreign)", value=True)
    exclude_y = st.checkbox("Exclude .Y (ADR)", value=True)
    exclude_q = st.checkbox("Exclude .Q (Bankruptcy)", value=True)

    st.divider()
    export_data = st.checkbox("📁 Enable Export to CSV", value=False)

# --------------------------------------
# Helpers
# --------------------------------------
def auto_grade(score):
    if pd.isna(score): return "?"
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"

def color_grade(val):
    colors = {
        "A+": "background-color: #00aa00; color: white",
        "A":  "background-color: #33aa33; color: white",
        "B":  "background-color: #88cc44; color: black",
        "C":  "background-color: #ffcc00; color: black",
        "D":  "background-color: #ff8800; color: black",
        "F":  "background-color: #cc0000; color: white",
        "?":  "background-color: #dddddd; color: black"
    }
    return colors.get(val, "")

def enhance_with_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Score" not in df.columns:
        df["Score"] = None
    if "Grade" not in df.columns:
        df["Grade"] = df["Score"].apply(auto_grade)
    else:
        df["Grade"] = df["Grade"].fillna(df["Score"].apply(auto_grade))
    return df

# --------------------------------------
# Cached Data Loader
# --------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(days, yield_pct, f, y, q, strict, use_db):
    if use_db:
        df = load_filtered_dividends(min_yield=yield_pct, days_ahead=days)
        return df, df
    else:
        live = get_upcoming_dividends(days_ahead=days, strict_filtering=strict)
        if live.empty:
            return live, pd.DataFrame()
        filtered = apply_filters(live, min_yield=yield_pct, exclude_f=f, exclude_y=y, exclude_q=q, strict_filtering=strict)
        return live, filtered

# --------------------------------------
# Load & Display Results
# --------------------------------------
with st.spinner("🔎 Analyzing upcoming dividend opportunities..."):
    all_data, filtered_data = fetch_data(
        days=days_ahead,
        yield_pct=min_yield,
        f=exclude_f,
        y=exclude_y,
        q=exclude_q,
        strict=strict_filtering,
        use_db=(data_source == "PostgreSQL Cache")
    )

if all_data.empty:
    st.warning("⚠️ No dividend data found. Adjust your filters or check back later.")
else:
    st.markdown(f"**Total tickers retrieved:** {len(all_data)}")

    if filtered_data.empty:
        st.info("No stocks meet your selected filters.")
        with st.expander("📋 Show all retrieved stocks"):
            st.dataframe(all_data.reset_index(drop=True))
    else:
        st.success(f"✅ {len(filtered_data)} stocks match your criteria:")

        display_df = enhance_with_scores(filtered_data)
        display_df = display_df.sort_values(by="Score", ascending=False, na_position="last")

        try:
            styled_df = display_df.style \
                .background_gradient(subset=["Score"], cmap="RdYlGn") \
                .applymap(color_grade, subset=["Grade"])
            st.dataframe(styled_df, use_container_width=True)
        except ImportError:
            st.warning("⚠️ `matplotlib` is required for gradient styling. Run `pip install matplotlib` to enable full styling.")
            st.dataframe(display_df, use_container_width=True)

        if export_data:
            csv = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Filtered Results as CSV",
                data=csv,
                file_name="filtered_dividend_picks.csv",
                mime="text/csv"
            )