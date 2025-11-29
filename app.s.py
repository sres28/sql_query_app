import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Dynamic SQL Builder", layout="wide")
st.title("🧩 Dynamic SQL Query Builder")

# ------------------------------
# UPLOAD CSV
# ------------------------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV Loaded Successfully!")
    st.dataframe(df.head())

    conn = sqlite3.connect(":memory:")
    df.to_sql("mytable", conn, index=False, if_exists="replace")

    columns = df.columns.tolist()

    st.markdown("---")
    st.header("Build Your SQL Query")

    # --------------------------
    # SELECT SECTION
    # --------------------------
    select_cols = st.multiselect("SELECT Columns", columns, default=columns)

    if not select_cols:
        st.warning("Select at least one column")
        st.stop()

    # --------------------------
    # WHERE CONDITIONS
    # --------------------------
    st.subheader("WHERE Conditions")

    if "conditions" not in st.session_state:
        st.session_state.conditions = []

    if st.button("➕ Add Condition"):
        st.session_state.conditions.append({"col": columns[0], "op": "=", "val": ""})

    new_conditions = []
    for i, cond in enumerate(st.session_state.conditions):
        c1, c2, c3, c4 = st.columns([2,1.5,2,1])

        col = c1.selectbox("Column", columns, key=f"col{i}", index=columns.index(cond["col"]))
        op = c2.selectbox("Operator", ["=", ">", "<", ">=", "<=", "LIKE", "IN"], key=f"op{i}", index=0)
        val = c3.text_input("Value", key=f"val{i}", value=cond["val"])

        delete = c4.button("❌", key=f"del{i}")

        if not delete:
            new_conditions.append({"col": col, "op": op, "val": val})

    st.session_state.conditions = new_conditions

    # --------------------------
    # ORDER BY
    # --------------------------
    st.subheader("Order By")
    order_col = st.selectbox("Order by column (optional)", ["None"] + columns)
    order_dir = st.radio("Order direction", ["ASC", "DESC"])

    # --------------------------
    # GROUP BY
    # --------------------------
    st.subheader("Group By (optional)")
    group_by = st.selectbox("Group by column", ["None"] + columns)

    # --------------------------
    # LIMIT
    # --------------------------
    limit = st.number_input("Limit Rows", min_value=1, max_value=10000, value=100)

    st.markdown("---")
    st.header("SQL Preview")

    # --------------------------
    # BUILD SQL QUERY
    # --------------------------
    query = f"SELECT {', '.join(select_cols)} FROM mytable"

    # WHERE
    if st.session_state.conditions:
        where_parts = []
        for c in st.session_state.conditions:
            if c["op"] == "IN":
                vals = ", ".join([f"'{v.strip()}'" for v in c["val"].split(",")])
                where_parts.append(f"{c['col']} IN ({vals})")
            else:
                where_parts.append(f"{c['col']} {c['op']} '{c['val']}'")
        query += " WHERE " + " AND ".join(where_parts)

    # GROUP BY
    if group_by != "None":
        query += f" GROUP BY {group_by}"

    # ORDER BY
    if order_col != "None":
        query += f" ORDER BY {order_col} {order_dir}"

    # LIMIT
    query += f" LIMIT {limit}"

    st.code(query, language="sql")

    # --------------------------
    # RUN QUERY
    # --------------------------
    st.markdown("### Run Query")

    if st.button("▶️ Execute Query"):
        try:
            result = pd.read_sql_query(query, conn)
            st.dataframe(result)
        except Exception as e:
            st.error(f"Error running SQL: {e}")
