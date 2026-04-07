import streamlit as st
import requests
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

# ---------- CONFIG & KEYS ----------
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
DB_NAME = "database.db"

# ---------- DATABASE ENGINE ----------
def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS STUDENT (
            NAME TEXT, COURSE TEXT, SECTION TEXT, MARKS INTEGER
        )
    """)
    cursor = conn.execute("SELECT COUNT(*) FROM STUDENT")
    if cursor.fetchone()[0] == 0:
        # Initial Sample Data
        data = [
            ("Alice", "Data Science", "A", 85),
            ("Bob", "Commerce", "B", 72),
            ("Charlie", "Data Science", "A", 90),
            ("David", "Science", "C", 65)
        ]
        conn.executemany("INSERT INTO STUDENT VALUES (?, ?, ?, ?)", data)
        conn.commit()
    conn.close()

init_db()

# ---------- AI LOGIC (Your Exact Prompt) ----------
def generate_sql(question):
    prompt = f"""
You are an expert SQL query generator.
Your task is to convert natural language questions into valid SQL queries.

DATABASE SCHEMA:
The database name is STUDENT and contains the following columns:
- NAME (text)
- COURSE (text)
- SECTION (text)
- MARKS (integer)

STRICT RULES:
1.If the user input is a greeting (hi, hello), gibberish (abc, asdf), or unrelated to data (what's the weather?), output exactly: "INVALID_INPUT"
2.Output ONLY the SQL query.
3.Do NOT include explanations, comments, or formatting.
4.Do NOT wrap the query in backticks (`) or markdown.
5.Do NOT include the word "sql" in output.
6.Always use correct SQL syntax.
7.Always use the STUDENT table unless specified otherwise.
8.Column names must match EXACTLY as given: NAME, COURSE, SECTION, MARKS
9.Strings must be enclosed in single quotes (' ').
10.Use uppercase for SQL keywords.

User Question: {question}
SQL:
"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "arcee-ai/trinity-large-preview:free",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}"

# ---------- UI LAYOUT ----------
st.set_page_config(page_title="Text2SQL", layout="wide", page_icon="💻")

# Sidebar Configuration
with st.sidebar:
    st.title("Settings & Docs")
    st.info("""
    **Project:** Text2SQL Engine  
    **Sample Dataset:** Student Records  
    **Model:** Trinity-Large (LLM)
    """)
    st.markdown("---")
    st.markdown("### Schema Explorer")
    st.code("Table: STUDENT\n- NAME (STR)\n- COURSE (STR)\n- SECTION (STR)\n- MARKS (INT)")

# Main Interface
st.title("Text2SQL")
st.write("Translate natural language into executable SQL queries in real-time.")

tab1, tab2, tab3 = st.tabs(["Query Engine", "Data Explorer", "Database Control"])

# --- TAB 1: QUERY ENGINE ---
with tab1:
    st.header("Natural Language to SQL")
    q = st.text_input("Enter your request in English:", placeholder="e.g., Which students in Section A have marks above 80?")
    
    if q:
        with st.spinner("Translating..."):
            sql = generate_sql(q)
            
        st.subheader("Generated SQL Output")
        st.code(sql, language="sql")
        
        if "SELECT" in sql.upper():
            try:
                conn = get_connection()
                df = pd.read_sql_query(sql, conn)
                st.subheader("Query Results")
                st.dataframe(df, use_container_width=True)
                conn.close()
            except Exception as e:
                st.error(f"Execution Error: {e}")
        else:
            st.warning("Note: The generated query is not a standard SELECT statement. Use 'Database Control' for data manipulation.")

# --- TAB 2: DATA EXPLORER ---
with tab2:
    st.header("Current Environment State")
    st.write("This tab displays the current raw state of the `STUDENT` sample database.")
    conn = get_connection()
    full_df = pd.read_sql_query("SELECT * FROM STUDENT", conn)
    st.dataframe(full_df, use_container_width=True)
    conn.close()
    
    if st.button("Refresh View"):
        st.rerun()

# --- TAB 3: DATABASE CONTROL (CRUD) ---
with tab3:
    st.header("Direct Data Manipulation")
    st.write("Manually edit the sample database to test edge cases.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Insert Record")
        with st.form("insert_form", clear_on_submit=True):
            name = st.text_input("Student Name")
            course = st.text_input("Course Name")
            section = st.selectbox("Section", ["A", "B", "C"])
            marks = st.number_input("Marks", 0, 100, 70)
            if st.form_submit_button("Execute INSERT"):
                conn = get_connection()
                conn.execute("INSERT INTO STUDENT VALUES (?, ?, ?, ?)", (name, course, section, marks))
                conn.commit()
                conn.close()
                st.success(f"Record for {name} committed to database.")

    with col2:
        st.subheader("Delete Record")
        conn = get_connection()
        current_names = [row[0] for row in conn.execute("SELECT NAME FROM STUDENT").fetchall()]
        conn.close()
        
        target = st.selectbox("Select Name to Remove", current_names)
        if st.button("Execute DELETE", type="primary"):
            conn = get_connection()
            conn.execute("DELETE FROM STUDENT WHERE NAME = ?", (target,))
            conn.commit()
            conn.close()
            st.warning(f"Record for {target} removed.")
            st.rerun()

st.divider()
st.caption("Text2SQL | Prabhnoor Singh")