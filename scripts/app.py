import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import base64
import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# --- Setup ---
SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

EXCEL_FILE = os.path.join(DATA_DIR, "Recipebase.xlsx")
logo_path = os.path.join(DATA_DIR, "Lifecode_Logo.png")

APPROVED_SKU_LIST = [
    "Almonds (Whole)", "Sunflower Seed (Whole)", "Pumpkin Seed (Whole)",
    "Black Raisins (Whole)", "Cashew (Whole)", "Dates (Whole)", "Raisins (Whole)",
    "Walnut (Whole)", "Toor Dal Arhar Split", "Black Pepper (Whole)", "Turmeric",
    "Cold Pressed Sesame Oil White", "Mustard (Whole)", "Cumin (Whole)", "Dry Red Chilli",
    "Garlic", "Curry Leaves", "Coriander Leaves", "Salt", "Water"
]

PRICE_DICT = {
    "Almonds (Whole)": 940, "Sunflower Seed (Whole)": 130, "Pumpkin Seed (Whole)": 530,
    "Black Raisins (Whole)": 195, "Cashew (Whole)": 1000, "Dates (Whole)": 250,
    "Raisins (Whole)": 195, "Walnut (Whole)": 1370, "Toor Dal Arhar Split": 155,
    "Black Pepper (Whole)": 950, "Turmeric": 210, "Cold Pressed Sesame Oil White": 310,
    "Mustard (Whole)": 120, "Cumin (Whole)": 365, "Dry Red Chilli": 320,
    "Garlic": 0, "Curry Leaves": 0, "Coriander Leaves": 0, "Salt": 0, "Water": 0
}

# --- Helpers ---
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def normalize_recipe_name(name):
    try:
        return transliterate(name.strip().lower(), sanscript.ITRANS, sanscript.TAMIL).strip()
    except:
        return name.strip().lower()

# --- Excel Handling ---
def load_memory():
    try:
        df = pd.read_excel(EXCEL_FILE)
        if "Recipe_Name_Tamil" not in df.columns:
            df["Recipe_Name_Tamil"] = df["Recipe_Name"].apply(normalize_recipe_name)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Recipe_Name", "Recipe_Name_Tamil", "Standard_Portion_Assumed_(Per_Person)",
            "Ingredients_(with_unit_quantity)", "Organic_Grocery_Required_(Per_Person)",
            "Grocery_Didn’t_Match_(if_any)", "Suitable_Accompaniment_(if_any)",
            "Total_Cost_(₹_Per_Person)", "Response"
        ])

def save_to_memory(df):
    df.to_excel(EXCEL_FILE, index=False)

# --- Validators ---
def match_skus(ingredient_lines):
    matched, unmatched = [], []
    for line in ingredient_lines:
        name = line.split("-")[0].strip() if "-" in line else line.strip()
        (matched if name in APPROVED_SKU_LIST else unmatched).append(line)
    return matched, unmatched

def calculate_cost(matched_lines):
    total = 0.0
    for line in matched_lines:
        if "-" not in line:
            continue
        try:
            name, qty_unit = map(str.strip, line.split("-", 1))
            qty_match = re.search(r'(\d+(\.\d+)?)\s*([a-zA-Z]+)', qty_unit)
            if not qty_match:
                continue
            qty, unit = float(qty_match[1]), qty_match[3].lower()
            price = PRICE_DICT.get(name, 0)
            total += (price / 1000) * qty if unit in ["g", "ml"] else price * qty
        except:
            continue
    return f"₹{total:.2f}"

# --- Core Logic ---
def get_recipe(dish_name, api_key):
    df = load_memory()
    input_tamil = normalize_recipe_name(dish_name)

    if "Recipe_Name_Tamil" in df.columns:
        match = df[df["Recipe_Name_Tamil"] == input_tamil]
        if not match.empty:
            return match.iloc[0], False

    # Gemini fallback
    approved_list = '\n'.join([f"• {item}" for item in APPROVED_SKU_LIST])
    prices_text = '\n'.join([f"• {item} – ₹{PRICE_DICT[item]}/kg or /L" for item in PRICE_DICT])

    prompt = f"""
You are a wise and experienced 60+ year old Chettinad chef working for a modern nutrition brand called Lifecode.
Your task is to prepare precise traditional Tamil recipes using only the below grocery items and their prices.
You must not invent new ingredients or use different names.
====================
📦 APPROVED INGREDIENTS
====================
{approved_list}
====================
💰 INGREDIENT PRICES
====================
{prices_text}
====================
🎯 OUTPUT FORMAT (MUST FOLLOW EXACTLY)
====================
1. Recipe Name (traditional Tamil): [Recipe Name here]
2. Standard Portion Assumed (Per Person):
    • Yield – ___ g cooked
    • Calories – ___ kcal approx.
    • Quantity – Approx. ___
3. Ingredients (with unit quantity):
    • [Ingredient - quantity unit]
4. Organic Grocery Required (Per Person):
    • [Matched Grocery - quantity unit]
5. Grocery Didn’t Match (if any):
    • [Unmatched Grocery - quantity unit] or "• Not applicable"
6. Suitable Accompaniment (if any): [Details here]
7. Total Cost (₹ Per Person): [Cost here]
8. Response:
    1. [Step 1]
    2. [Step 2]
Dish Name: {dish_name}
Only use g/ml units. Never use cups, spoons, pinch, etc. Stick to the above SKU list only.
"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        chat = model.start_chat()
        result = chat.send_message(prompt)
        response = result.text or result.candidates[0].content.parts[0].text
    except Exception as e:
        st.error(f"❌ Gemini call failed: {e}")
        return None, False

    column_mapping = {
        "1. Recipe Name": "Recipe_Name",
        "2. Standard Portion Assumed": "Standard_Portion_Assumed_(Per_Person)",
        "3. Ingredients": "Ingredients_(with_unit_quantity)",
        "4. Organic Grocery Required": "Organic_Grocery_Required_(Per_Person)",
        "5. Grocery Didn’t Match": "Grocery_Didn’t_Match_(if_any)",
        "6. Suitable Accompaniment": "Suitable_Accompaniment_(if_any)",
        "7. Total Cost": "Total_Cost_(₹_Per_Person)",
        "8. Response": "Response"
    }

    parsed_data, current_key, current_lines = {}, None, []
    lines = response.strip().splitlines()
    heading_pattern = re.compile(r"^\s*(\d+\.\s*[A-Za-z\s’‘“”()]+):\s*(.*)")

    for line in lines:
        match = heading_pattern.match(line.strip())
        if match:
            if current_key:
                parsed_data[current_key] = "\n".join(current_lines).strip()
            heading = match.group(1).strip()
            content = match.group(2).strip()
            current_key = column_mapping.get(heading, heading)
            current_lines = [content]
        else:
            current_lines.append(line.strip())

    if current_key:
        parsed_data[current_key] = "\n".join(current_lines).strip()

    final_values = {col: "" for col in df.columns}
    final_values.update(parsed_data)
    final_values["Recipe_Name"] = dish_name
    final_values["Recipe_Name_Tamil"] = input_tamil

    ing_lines = final_values.get("Ingredients_(with_unit_quantity)", "").split("\n")
    matched, unmatched = match_skus(ing_lines)
    final_values["Organic_Grocery_Required_(Per_Person)"] = "\n".join(matched)
    final_values["Grocery_Didn’t_Match_(if_any)"] = "\n".join(unmatched) if unmatched else "• Not applicable"
    final_values["Total_Cost_(₹_Per_Person)"] = calculate_cost(matched)

    df = pd.concat([df, pd.DataFrame([final_values])], ignore_index=True)
    save_to_memory(df)
    return df.iloc[-1], True

# --- Streamlit UI ---
st.set_page_config(page_title="🧬 Lifecode Recipe Generator", layout="centered")
st.title("🍛 Lifecode Recipe Generator")

api_key = st.text_input("🔑 Enter your Gemini API Key:", type="password")

if api_key:
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
            with st.spinner("Sourcing wisdom from our traditional kitchens..."):
                row, is_new = get_recipe(user_input, api_key)
                if row is None:
                    st.error("Could not retrieve recipe.")
                else:
                    msg = f"<p style='color:#007bff; font-style:italic;'>"
                    msg += '👨‍🍳 Freshly prepared by Lifecode Chef!' if is_new else '📒 Lifecode Chef remembered this one!'
                    msg += "</p>\n\n"
                    msg += f"## {row['Recipe_Name']}\n\n"
                    msg += f"### Portion Details\n{row['Standard_Portion_Assumed_(Per_Person)']}\n\n"
                    msg += f"### Ingredients\n{row['Ingredients_(with_unit_quantity)']}\n\n"
                    msg += f"### Preparation Steps\n{row['Response']}\n\n"
                    if row['Suitable_Accompaniment_(if_any)'] not in ["", "Not applicable", "n/a"]:
                        msg += f"### Suitable Accompaniment\n{row['Suitable_Accompaniment_(if_any)']}\n\n"
                    msg += f"### Estimated Cost\n{row['Total_Cost_(₹_Per_Person)']}\n\n"
                    st.markdown(msg, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
else:
    st.info("Please enter your Gemini API key to begin.")
