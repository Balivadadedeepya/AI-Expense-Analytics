import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Expense Analytics",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .metric-card {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, #172033, #202b40);
        text-align: center;
        border: 1px solid #303b52;
    }

    .metric-title {
        font-size: 15px;
        color: #aab4c3;
    }

    .metric-value {
        font-size: 30px;
        font-weight: bold;
        color: #ffffff;
    }

    .insight-box {
        padding: 18px;
        border-radius: 12px;
        background-color: #172033;
        border-left: 5px solid #00c2ff;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("💰 AI Expense Analytics")
st.markdown(
    "### 📊 Track spending • Discover patterns • Generate financial insights"
)

st.markdown("---")

# ---------------------------------------------------------
# SAMPLE DATA
# ---------------------------------------------------------

sample_data = pd.DataFrame({
    "Date": pd.to_datetime([
        "2026-01-03", "2026-01-05", "2026-01-10",
        "2026-01-15", "2026-01-20", "2026-02-02",
        "2026-02-08", "2026-02-14", "2026-02-20",
        "2026-03-01", "2026-03-05", "2026-03-12"
    ]),
    "Category": [
        "Food", "Transport", "Shopping",
        "Bills", "Entertainment", "Food",
        "Shopping", "Transport", "Bills",
        "Food", "Entertainment", "Shopping"
    ],
    "Amount": [
        450, 200, 1500,
        1200, 600, 700,
        1800, 300, 1300,
        550, 800, 2100
    ],
    "Description": [
        "Restaurant", "Bus", "Clothes",
        "Electricity", "Movie", "Groceries",
        "Online Shopping", "Cab", "Internet",
        "Restaurant", "Games", "Online Shopping"
    ]
})

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.header("⚙️ Data Options")

data_source = st.sidebar.radio(
    "Choose data source",
    ["Use Sample Data", "Upload CSV", "Add Expenses Manually"]
)

# ---------------------------------------------------------
# USE SAMPLE DATA
# ---------------------------------------------------------

if data_source == "Use Sample Data":

    df = sample_data.copy()

# ---------------------------------------------------------
# UPLOAD CSV
# ---------------------------------------------------------

elif data_source == "Upload CSV":

    uploaded_file = st.sidebar.file_uploader(
        "Upload expense CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            df = pd.read_csv(uploaded_file)

            required_columns = ["Date", "Category", "Amount"]

            missing_columns = [
                column for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:
                st.error(
                    f"Missing required columns: {', '.join(missing_columns)}"
                )
                st.stop()

            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

            df = df.dropna(subset=["Date", "Amount", "Category"])

        except Exception as error:
            st.error(f"Could not read the CSV file: {error}")
            st.stop()

    else:
        st.info(
            "Upload a CSV file or select 'Use Sample Data' from the sidebar."
        )
        st.stop()

# ---------------------------------------------------------
# MANUAL EXPENSE ENTRY
# ---------------------------------------------------------

else:

    st.sidebar.subheader("➕ Add Expense")

    if "manual_expenses" not in st.session_state:
        st.session_state.manual_expenses = []

    expense_date = st.sidebar.date_input(
        "Date"
    )

    category = st.sidebar.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Shopping",
            "Bills",
            "Entertainment",
            "Education",
            "Health",
            "Travel",
            "Other"
        ]
    )

    amount = st.sidebar.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=50.0
    )

    description = st.sidebar.text_input(
        "Description"
    )

    if st.sidebar.button("Add Expense"):

        if amount <= 0:
            st.sidebar.warning("Enter an amount greater than ₹0.")
        else:

            st.session_state.manual_expenses.append({
                "Date": pd.Timestamp(expense_date),
                "Category": category,
                "Amount": amount,
                "Description": description
            })

            st.sidebar.success("Expense added!")

    if st.session_state.manual_expenses:

        df = pd.DataFrame(st.session_state.manual_expenses)

    else:

        df = sample_data.copy()

        st.info(
            "No manual expenses added yet. Sample data is being displayed."
        )

# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

df = df.dropna(subset=["Date", "Amount", "Category"])

df["Category"] = df["Category"].astype(str).str.strip()

df["Month"] = df["Date"].dt.strftime("%b %Y")

df["Month_Number"] = df["Date"].dt.to_period("M")

df = df.sort_values("Date")

# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------

total_spending = df["Amount"].sum()

average_expense = df["Amount"].mean()

number_of_transactions = len(df)

highest_expense = df["Amount"].max()

highest_category = (
    df.groupby("Category")["Amount"]
    .sum()
    .idxmax()
)

highest_category_amount = (
    df.groupby("Category")["Amount"]
    .sum()
    .max()
)

# ---------------------------------------------------------
# KPI DASHBOARD
# ---------------------------------------------------------

st.subheader("📊 Financial Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">💰 Total Spending</div>
            <div class="metric-value">₹{total_spending:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">📈 Average Expense</div>
            <div class="metric-value">₹{average_expense:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">🧾 Transactions</div>
            <div class="metric-value">{number_of_transactions}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">🔥 Highest Expense</div>
            <div class="metric-value">₹{highest_expense:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------------------------------------------------------
# CATEGORY ANALYSIS
# ---------------------------------------------------------

st.subheader("🏷️ Spending by Category")

category_summary = (
    df.groupby("Category", as_index=False)["Amount"]
    .sum()
    .sort_values("Amount", ascending=False)
)

col1, col2 = st.columns(2)

with col1:

    fig_category = px.bar(
        category_summary,
        x="Category",
        y="Amount",
        title="Total Spending by Category",
        labels={
            "Amount": "Spending (₹)",
            "Category": "Category"
        },
        text_auto=".0f"
    )

    fig_category.update_layout(
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

with col2:

    fig_pie = px.pie(
        category_summary,
        names="Category",
        values="Amount",
        title="Expense Distribution",
        hole=0.45
    )

    fig_pie.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# ---------------------------------------------------------
# MONTHLY ANALYSIS
# ---------------------------------------------------------

st.subheader("📅 Monthly Spending Trend")

monthly_summary = (
    df.groupby("Month_Number")["Amount"]
    .sum()
    .reset_index()
    .sort_values("Month_Number")
)

monthly_summary["Month"] = (
    monthly_summary["Month_Number"]
    .astype(str)
)

fig_monthly = px.line(
    monthly_summary,
    x="Month",
    y="Amount",
    markers=True,
    title="Monthly Spending Trend"
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Spending (₹)",
    template="plotly_dark"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

# ---------------------------------------------------------
# TOP EXPENSES
# ---------------------------------------------------------

st.subheader("🔥 Top Expenses")

top_expenses = (
    df.sort_values("Amount", ascending=False)
    .head(5)
    .copy()
)

display_columns = [
    column for column in
    ["Date", "Category", "Amount", "Description"]
    if column in top_expenses.columns
]

st.dataframe(
    top_expenses[display_columns],
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# AUTOMATED INSIGHTS
# ---------------------------------------------------------

st.subheader("🧠 Automated Spending Insights")

category_percentage = (
    highest_category_amount / total_spending * 100
    if total_spending > 0
    else 0
)

insight_1 = (
    f"Your highest spending category is **{highest_category}**, "
    f"accounting for approximately **{category_percentage:.1f}%** "
    f"of your total spending."
)

st.markdown(
    f"""
    <div class="insight-box">
        💡 {insight_1}
    </div>
    """,
    unsafe_allow_html=True
)

if category_percentage > 40:

    message = (
        f"More than 40% of your spending is concentrated in "
        f"{highest_category}. Reviewing this category could help "
        f"reduce unnecessary expenses."
    )

else:

    message = (
        "Your spending is relatively distributed across categories. "
        "Continue monitoring the categories with the highest growth."
    )

st.markdown(
    f"""
    <div class="insight-box">
        📌 {message}
    </div>
    """,
    unsafe_allow_html=True
)

if average_expense > 1000:

    message = (
        "Your average transaction is above ₹1,000. "
        "Consider reviewing high-value purchases individually."
    )

else:

    message = (
        "Your average transaction is below ₹1,000, "
        "indicating relatively smaller individual expenses."
    )

st.markdown(
    f"""
    <div class="insight-box">
        📊 {message}
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# CATEGORY TABLE
# ---------------------------------------------------------

st.subheader("📋 Category Summary")

category_table = category_summary.copy()

category_table["Percentage"] = (
    category_table["Amount"] /
    total_spending *
    100
).round(2)

category_table["Amount"] = category_table["Amount"].round(2)

category_table = category_table.rename(
    columns={
        "Category": "Category",
        "Amount": "Total Spending (₹)",
        "Percentage": "Share (%)"
    }
)

st.dataframe(
    category_table,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# DOWNLOAD DATA
# ---------------------------------------------------------

st.subheader("📥 Export Data")

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Expense Data as CSV",
    data=csv_data,
    file_name="expense_analysis.csv",
    mime="text/csv"
)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "AI Expense Analytics • Built with Python, Pandas, Plotly and Streamlit"
)
