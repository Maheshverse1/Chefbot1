# --- Imports ---
import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import requests
import json
import re
import base64

# --- Global Paths ---
SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

EXCEL_FILE = os.path.join(DATA_DIR, "Recipebase.xlsx")
logo_path = os.path.join(DATA_DIR, "Lifecode_Logo.png")
CSS_FILE = os.path.join(SCRIPT_DIR, "style.css")

# --- Approved SKUs & Prices ---
APPROVED_SKU_LIST_RAW = [
    "Almonds (Whole)", "Sunflower Seed (Whole)", "Pumpkin Seed (Whole)",
    "Black Raisins (Whole)", "Cashew (Whole)", "Dates (Whole)", "Raisins (Whole)",
    "Walnut (Whole)", "Toor Dal Arhar Split", "Black Pepper (Whole)", "Turmeric",
    "Cold Pressed Sesame Oil White", "Mustard (Whole)", "Cumin (Whole)", "Dry Red Chilli",
    "Garlic", "Curry Leaves", "Coriander Leaves", "Salt", "Water"
]
APPROVED_SKU_LIST = {item.strip().lower() for item in APPROVED_SKU_LIST_RAW}

PRICE_DICT = {
    "Almonds (Whole)": 940, "Sunflower Seed (Whole)": 130, "Pumpkin Seed (Whole)": 530,
    "Black Raisins (Whole)": 195, "Cashew (Whole)": 1000, "Dates (Whole)": 250,
    "Raisins (Whole)": 195, "Walnut (Whole)": 1370, "Toor Dal Arhar Split": 155,
    "Black Pepper (Whole)": 950, "Turmeric": 210, "Cold Pressed Sesame Oil White": 310,
    "Mustard (Whole)": 120, "Cumin (Whole)": 365, "Dry Red Chilli": 320,
    "Garlic": 0, "Curry Leaves": 0, "Coriander Leaves": 0, "Salt": 0, "Water": 0
}
NORMALIZED_PRICE_DICT = {k.strip().lower(): v for k, v in PRICE_DICT.items()}

# --- Utilities ---
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def load_memory():
    try:
        return pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Recipe_Name",
            "Standard_Portion_Assumed_(Per_Person)",
            "Ingredients_(with_unit_quantity)",
            "Organic_Grocery_Required_(Per_Person)",
            "Grocery_Didn’t_Match_(if_any)",
            "Suitable_Accompaniment_(if_any)",
            "Total_Cost_(₹_Per_Person)",
            "Response"
        ])

# --- Streamlit UI ---
st.set_page_config(page_title="🧬 Lifecode Recipe Generator", layout="centered")

try:
    with open(CSS_FILE) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error(f"❌ CSS file not found at '{CSS_FILE}'. Please ensure 'style.css' is in the same directory as your script.")
except Exception as e:
    st.error(f"❌ Error loading CSS: {e}")

st.markdown("""
    <div class="main-header">
""", unsafe_allow_html=True)

if os.path.exists(logo_path):
    base64_logo = get_base64_image(logo_path)
    if base64_logo:
        st.markdown(f"""
            <div style='text-align: center;'>
                <img src='data:image/png;base64,{base64_logo}'>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Could not convert logo to base64. Image file might be corrupted or empty.")
else:
    st.warning("⚠️ Logo not found at 'data/Lifecode_Logo.png'")

st.markdown("""
        <h1>🍛 Lifecode Recipe Generator</h1>
        <p>From Insight to Foresight: Traditional Tamil recipes with modern precision</p>
    </div>
""", unsafe_allow_html=True)

# --- Main Chat Section ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if user_input := st.chat_input("Which Tamil recipe would you like today?"):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching Lifecode Chef's memory..."):
            df = load_memory()
            match_row = df[df["Recipe_Name"].str.strip().str.lower() == user_input.strip().lower()]

            if not match_row.empty:
                row = match_row.iloc[0]
                recipe_name = str(row["Recipe_Name"] or '').strip()
                portion_details = str(row["Standard_Portion_Assumed_(Per_Person)"] or '').strip()
                ingredients = str(row["Ingredients_(with_unit_quantity)"] or '').strip()
                preparation_steps = str(row["Response"] or '').strip()
                accompaniment = str(row["Suitable_Accompaniment_(if_any)"] or '').strip()
                total_cost = str(row["Total_Cost_(₹_Per_Person)"] or '').strip()

                response_md = """
<p style='color:#007bff; font-style:italic;'>📒 Lifecode Chef remembered this one!</p>
"""
                response_md += f"## {recipe_name}\n\n"

                if portion_details:
                    response_md += "### Portion Details\n" + portion_details + "\n\n"
                if ingredients:
                    response_md += "### Ingredients\n" + ingredients + "\n\n"
                if preparation_steps:
                    response_md += "### Preparation Steps\n" + preparation_steps + "\n\n"
                if accompaniment.lower() not in ["not applicable", "n/a", ""]:
                    response_md += "### Suitable Accompaniment\n" + accompaniment + "\n\n"
                if total_cost:
                    response_md += "### Estimated Cost\n" + total_cost + "\n\n"

                st.markdown(response_md, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response_md})
            else:
                st.markdown("❌ Recipe not found in local memory. Please try again later.")
