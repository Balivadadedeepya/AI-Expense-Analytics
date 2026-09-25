import sqlite3
from datetime import date

import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Expense Analytics",
    page_icon="💰",
    layout="wide"
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

DB_NAME = "expenses.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def initialize_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


initialize_database()


# ---------------------------------------------------------
# DATABASE FUNCTIONS
# ---------------------------------------------------------

def add_transaction(transaction_date, description, category, transaction_type, amount):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO transactions
        (transaction_date, description, category, transaction_type, amount)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(transaction_date),
            description,
            category,
            transaction_type,
            amount
        )
    )

    conn.commit()
    conn.close()


def delete_transaction(transaction_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    conn.commit()
    conn.close()


def load_transactions():
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            id,
            transaction_date,
            description,
            category,
            transaction_type,
            amount
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
        """,
        conn
    )

    conn.close()

    if not df.empty:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
        df["amount"] = pd.to_numeric(df["amount"])

    return df


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("💰 AI Expense Analytics")
st.markdown(
    "### Track spending, analyze financial patterns, and discover unusual transactions."
)

st.divider()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("⚙️ Add Transaction")

transaction_date = st.sidebar.date_input(
    "Date",
    value=date.today()
)

description = st.sidebar.text_input(
    "Description",
    placeholder="e.g. Grocery shopping"
)

category = st.sidebar.selectbox(
    "Category",
    [
        "Food",
        "Shopping",
        "Transport",
        "Bills",
        "Entertainment",
        "Health",
        "Education",
        "Travel",
        "Salary",
        "Investment",
        "Other"
    ]
)

transaction_type = st.sidebar.selectbox(
    "Transaction Type",
    ["Expense", "Income"]
)

amount = st.sidebar.number_input(
    "Amount",
    min_value=0.01,
    step=100.0,
    format="%.2f"
)

if st.sidebar.button("➕ Add Transaction", use_container_width=True):

    if description.strip() == "":
        st.sidebar.error("Please enter a description.")

    elif amount <= 0:
        st.sidebar.error("Amount must be greater than zero.")

    else:
        add_transaction(
            transaction_date,
            description.strip(),
            category,
            transaction_type,
            amount
        )

        st.sidebar.success("Transaction added successfully!")
        st.rerun()


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

df = load_transactions()


# ---------------------------------------------------------
# EMPTY STATE
# ---------------------------------------------------------

if df.empty:

    st.info(
        "👋 Welcome! Add your first transaction using the sidebar "
        "to start analyzing your finances."
    )

    st.markdown("### What this dashboard provides")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📊 Analytics")
        st.write("Understand where your money goes.")

    with col2:
        st.markdown("#### 📈 Trends")
        st.write("Track spending patterns over time.")

    with col3:
        st.markdown("#### 🚨 Anomaly Detection")
        st.write("Identify unusually large transactions.")

    st.stop()


# ---------------------------------------------------------
# FINANCIAL METRICS
# ---------------------------------------------------------

income = df.loc[
    df["transaction_type"] == "Income",
    "amount"
].sum()

expenses = df.loc[
    df["transaction_type"] == "Expense",
    "amount"
].sum()

balance = income - expenses

transaction_count = len(df)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💵 Total Income",
        f"₹{income:,.2f}"
    )

with col2:
    st.metric(
        "💸 Total Expenses",
        f"₹{expenses:,.2f}"
    )

with col3:
    st.metric(
        "💰 Balance",
        f"₹{balance:,.2f}"
    )

with col4:
    st.metric(
        "🧾 Transactions",
        transaction_count
    )


st.divider()


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------

st.subheader("🔎 Filter Transactions")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    selected_category = st.multiselect(
        "Category",
        sorted(df["category"].unique())
    )

with filter_col2:
    selected_type = st.multiselect(
        "Type",
        ["Income", "Expense"]
    )

with filter_col3:
    search_text = st.text_input(
        "Search",
        placeholder="Search description..."
    )


filtered_df = df.copy()

if selected_category:
    filtered_df = filtered_df[
        filtered_df["category"].isin(selected_category)
    ]

if selected_type:
    filtered_df = filtered_df[
        filtered_df["transaction_type"].isin(selected_type)
    ]

if search_text:
    filtered_df = filtered_df[
        filtered_df["description"]
        .str.contains(search_text, case=False, na=False)
    ]


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

st.subheader("📊 Spending Dashboard")

expense_df = df[
    df["transaction_type"] == "Expense"
].copy()


chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    st.markdown("#### Spending by Category")

    if not expense_df.empty:

        category_data = (
            expense_df
            .groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_data)

    else:
        st.info("No expense data available.")


with chart_col2:

    st.markdown("#### Monthly Spending Trend")

    if not expense_df.empty:

        monthly_data = (
            expense_df
            .assign(
                month=expense_df["transaction_date"].dt.to_period("M")
            )
            .groupby("month")["amount"]
            .sum()
        )

        monthly_data.index = monthly_data.index.astype(str)

        st.line_chart(monthly_data)

    else:
        st.info("No expense data available.")


st.divider()


# ---------------------------------------------------------
# SPENDING INSIGHTS
# ---------------------------------------------------------

st.subheader("💡 Spending Insights")

if not expense_df.empty:

    highest_category = (
        expense_df.groupby("category")["amount"]
        .sum()
        .idxmax()
    )

    highest_amount = (
        expense_df.groupby("category")["amount"]
        .sum()
        .max()
    )

    average_expense = expense_df["amount"].mean()

    insight_col1, insight_col2, insight_col3 = st.columns(3)

    with insight_col1:
        st.metric(
            "Highest Spending Category",
            highest_category
        )

    with insight_col2:
        st.metric(
            "Category Spending",
            f"₹{highest_amount:,.2f}"
        )

    with insight_col3:
        st.metric(
            "Average Expense",
            f"₹{average_expense:,.2f}"
        )

    if income > 0:

        savings_rate = (
            (income - expenses) / income
        ) * 100

        st.info(
            f"Your current income-to-expense calculation gives a "
            f"savings rate of **{savings_rate:.1f}%**."
        )

    st.write(
        f"Your largest spending category is **{highest_category}** "
        f"with total spending of **₹{highest_amount:,.2f}**."
    )

else:

    st.info("Add expense transactions to generate insights.")


# ---------------------------------------------------------
# ANOMALY DETECTION
# ---------------------------------------------------------

st.divider()

st.subheader("🚨 Unusual Spending Detection")

if len(expense_df) >= 5:

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    expense_df["anomaly"] = model.fit_predict(
        expense_df[["amount"]]
    )

    unusual = expense_df[
        expense_df["anomaly"] == -1
    ].copy()

    if unusual.empty:

        st.success(
            "No unusually large spending transactions were detected."
        )

    else:

        st.warning(
            f"{len(unusual)} potentially unusual transaction(s) detected."
        )

        display_columns = [
            "transaction_date",
            "description",
            "category",
            "amount"
        ]

        st.dataframe(
            unusual[display_columns],
            use_container_width=True,
            hide_index=True
        )

else:

    st.info(
        "Add at least 5 expense transactions to enable "
        "anomaly detection."
    )


# ---------------------------------------------------------
# TRANSACTION TABLE
# ---------------------------------------------------------

st.divider()

st.subheader("📋 Transactions")

if filtered_df.empty:

    st.info("No transactions match the selected filters.")

else:

    display_df = filtered_df.copy()

    display_df["transaction_date"] = (
        display_df["transaction_date"]
        .dt.strftime("%Y-%m-%d")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# DELETE TRANSACTION
# ---------------------------------------------------------

st.subheader("🗑️ Delete a Transaction")

if not df.empty:

    transaction_options = {
        f"{row['transaction_date'].strftime('%Y-%m-%d')} | "
        f"{row['description']} | "
        f"₹{row['amount']:,.2f}":
        int(row["id"])
        for _, row in df.iterrows()
    }

    selected_transaction = st.selectbox(
        "Select transaction",
        list(transaction_options.keys())
    )

    if st.button(
        "Delete Selected Transaction",
        type="secondary"
    ):

        transaction_id = transaction_options[
            selected_transaction
        ]

        delete_transaction(transaction_id)

        st.success("Transaction deleted successfully.")

        st.rerun()


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "AI Expense Analytics • Built with Python, Pandas, "
    "Scikit-learn, SQLite and Streamlit"
)
