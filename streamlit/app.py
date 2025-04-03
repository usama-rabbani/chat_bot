import streamlit as st
import pandas as pd
import requests
import openai
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- FUNCTION TO FETCH API DATA ----------
def fetch_data_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        
        if "application/json" in content_type:
            return pd.DataFrame(response.json())
        elif "text/csv" in content_type:
            from io import StringIO
            return pd.read_csv(StringIO(response.text))
        else:
            st.error("Unsupported API response format. Please provide JSON or CSV data.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ API Request Failed: {e}")
        return None

# ---------- FUNCTION TO GENERATE AI ANSWERS ----------
def generate_answer(df, question):
    df_string = df.to_csv(index=False)
    
    prompt = f"""
    You are an expert data analyst. Analyze the following data and answer the user's question.
    
    DATA:
    {df_string}
    
    QUESTION:
    {question}
    """

    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ API Error: {response.text}"

# ---------- STREAMLIT UI ----------
st.title("📊 Data Q&A with AI + Graphs (Powered by GPT-4o)")
uploaded_file = st.file_uploader("📂 Upload a file (CSV, JSON, XLSX):", type=["csv", "json", "xlsx"])
api_url = st.text_input("🔗 Enter an API endpoint to fetch data:")

df = None

if uploaded_file:
    st.write(f"File type detected: `{uploaded_file.type}`")
    try:
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.type == "application/json":
            df = pd.read_json(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type!")
    except Exception as e:
        st.error(f"Error loading file: {e}")

elif api_url:
    with st.spinner("Fetching data from API..."):
        df = fetch_data_from_api(api_url)

if df is not None:
    st.subheader("📄 Data Preview")
    st.write(df)
    
    # Graph Selection
    graph_type = st.selectbox("📊 Select a Graph Type:", ["None", "Histogram", "Boxplot", "Scatter Plot", "Line Chart"])
    column = st.selectbox("📌 Select a Column:", df.columns)
    
    if graph_type != "None":
        st.subheader(f"📈 {graph_type} of {column}")
        fig, ax = plt.subplots()
        
        if graph_type == "Histogram":
            sns.histplot(df[column], kde=True, ax=ax)
        elif graph_type == "Boxplot":
            sns.boxplot(y=df[column], ax=ax)
        elif graph_type == "Scatter Plot":
            col2 = st.selectbox("Select another column for Scatter Plot", df.columns)
            sns.scatterplot(x=df[column], y=df[col2], ax=ax)
        elif graph_type == "Line Chart":
            df[column].plot(kind="line", ax=ax)
        
        st.pyplot(fig)
    
    question = st.text_input("❓ Ask a question about your data:")
    if question:
        with st.spinner("AI is analyzing the data... 🤔"):
            answer = generate_answer(df, question)
        st.success("✅ Answer Ready!")
        st.subheader("📝 AI's Answer:")
        st.write(answer)

st.markdown("---")
st.markdown("Made with ❤️ using **GPT-4o** and Streamlit")
