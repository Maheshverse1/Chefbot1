# --- Imports ---
import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import re
import difflib
import base64
import json

# --- Global Paths ---
SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

EXCEL_FILE = os.path.join(DATA_DIR, "Recipebase.xlsx")
logo_path = os.path.join(DATA_DIR, "Lifecode_Logo.png")
CSS_FILE = os.path.join(SCRIPT_DIR, "style.css")

# --- Approved SKUs & Prices ---
APPROVED_SKU_LIST_RAW = ["Almonds (Whole)", "Sunflower Seed (Whole)", "Pumpkin Seed (Whole)", "Black Raisins (Whole)", "Cashew (Whole)", "Dates (Whole)", "Raisins (Whole)", "Walnut (Whole)", "Amaranth Flour Raw", "Bajra Flour Raw", "Bajra Pearl Millet", "Barnyard Millet Flour Raw", "Barnyard Millet Kuthiraivali", "Besan Flour Raw", "Foxtail Millet Flour", "Foxtail Millet Thinai", "Jowar Flour Raw", "Jowar Sorghum", "Khapli Wheat Flour", "Kodo Millet", "Kodo Millet Flour Raw", "Little Millet Flour", "Little Millet Samai", "Maize Flour", "Ragi Flour", "Ragi Millet", "Samai Little Millet", "Thinai Foxtail Millet", "Wheat Flour Raw", "A2 Ghee", "Cold Pressed Castor Oil", "Cold Pressed Coconut Oil", "Cold Pressed Groundnut Oil", "Cold Pressed Mustard Oil", "Cold Pressed Sesame Oil Black", "Cold Pressed Sesame Oil White", "Cold Pressed Sunflower Oil", "Black Urad Dal (Whole)", "Black Urad Dal Split", "Chana Bengal Gram", "Chana Dal Split", "Green Gram (Whole)", "Green Gram Dal Split", "Horsegram Kulthi", "Kabuli Chana", "Lobia Black Eyed Peas", "Masoor Dal (Whole)", "Masoor Dal Split", "Moong Dal (Whole)", "Moong Dal Split", "Rajma Red Kidney Beans", "Split Urad Dal Split With Skin", "Split Urad Dal Without Skin", "Toor Dal Arhar Split", "Urad Dal Black Gram Split", "White Urad Dal (Whole)", "Whole Moong", "Yellow Moong Dal Split", "Adai Mix", "Aval (Flattened Rice)", "Basmati Rice", "Black Rice", "Bpt Rice", "Broken Rice", "Brown Rice", "Hand Pounded Rice", "Idli Rice", "Karungkuruvai Rice", "Kitchili Samba Boiled Rice", "Kitchili Samba Rice", "Mapillai Samba Rice", "Matta Rice", "Parboiled Rice", "Ponni Rice Boiled", "Ponni Rice Raw", "Poongar Rice", "Red Poha", "Red Rice", "Rice Flour", "Seeraga Samba Rice", "Chia Seed (Whole)", "Flax Seed (Whole)", "Groundnuts", "Sesame Seed Black (Whole)", "Sesame Seed White (Whole)", "Ajwain (Powder)", "Ajwain (Whole)", "Bay Leaf", "Biryani Masala", "Black Cumin Kala Jeera", "Black Pepper (Powder)", "Black Pepper (Whole)", "Cardamom (Powder)", "Cardamom (Whole)", "Chaat Masala", "Cinnamon (Powder)", "Cinnamon (Whole)", "Clove (Powder)", "Clove (Whole)", "Coriander (Powder)", "Coriander (Whole)", "Cumin (Powder)", "Cumin (Whole)", "Dry Red Chilli", "Fennel (Powder)", "Fennel (Whole)", "Fenugreek (Powder)", "Fenugreek (Whole)", "Garam Masala", "Hing Asafoetida", "Mustard (Powder)", "Mustard (Whole)", "Rasam (Powder)", "Star Anise", "Turmeric", "Whole Red Chillies", "Brown Sugar", "Coconut Sugar", "Honey", "Jaggery (Powder)", "Jaggery (Solid)", "Palm Jaggery", "Stevia Leaf (Powder)", "CTC Tea", "Green Tea Leaf", "Organic Coffee Arabica", "Organic Coffee Robusta", "Sambar Powder"
]

PRICE_DICT = {
  "Almonds (Whole)": 940,
  "Sunflower Seed (Whole)": 130,
  "Pumpkin Seed (Whole)": 530,
  "Black Raisins (Whole)": 195,
  "Cashew (Whole)": 1000,
  "Dates (Whole)": 250,
  "Raisins (Whole)": 195,
  "Walnut (Whole)": 1370,
  "Amaranth Flour Raw": 145,
  "Bajra Flour Raw": 90,
  "Bajra Pearl Millet": 65,
  "Barnyard Millet Flour Raw": 92,
  "Barnyard Millet Kuthiraivali": 75,
  "Besan Flour Raw": 125,
  "Foxtail Millet Flour": 95,
  "Foxtail Millet Thinai": 85,
  "Jowar Flour Raw": 78,
  "Jowar Sorghum": 70,
  "Khapli Wheat Flour": 88,
  "Kodo Millet": 78,
  "Kodo Millet Flour Raw": 90,
  "Little Millet Flour": 92,
  "Little Millet Samai": 85,
  "Maize Flour": 80,
  "Ragi Flour": 92,
  "Ragi Millet": 78,
  "Samai Little Millet": 85,
  "Thinai Foxtail Millet": 85,
  "Wheat Flour Raw": 85,
  "A2 Ghee": 1044,
  "Cold Pressed Castor Oil": 260,
  "Cold Pressed Coconut Oil": 340,
  "Cold Pressed Groundnut Oil": 259,
  "Cold Pressed Mustard Oil": 331,
  "Cold Pressed Sesame Oil Black": 340,
  "Cold Pressed Sesame Oil White": 310,
  "Cold Pressed Sunflower Oil": 245,
  "Black Urad Dal (Whole)": 162,
  "Black Urad Dal Split": 165,
  "Chana Bengal Gram": 120,
  "Chana Dal Split": 115,
  "Green Gram (Whole)": 142,
  "Green Gram Dal Split": 130,
  "Horsegram Kulthi": 95,
  "Kabuli Chana": 215,
  "Lobia Black Eyed Peas": 150,
  "Masoor Dal (Whole)": 105,
  "Masoor Dal Split": 106,
  "Moong Dal (Whole)": 142,
  "Moong Dal Split": 130,
  "Rajma Red Kidney Beans": 140,
  "Split Urad Dal Split With Skin": 165,
  "Split Urad Dal Without Skin": 170,
  "Toor Dal Arhar Split": 155,
  "Urad Dal Black Gram Split": 165,
  "White Urad Dal (Whole)": 168,
  "Whole Moong": 142,
  "Yellow Moong Dal Split": 132,
  "Adai Mix": 110,
  "Aval (Flattened Rice)": 85,
  "Basmati Rice": 108,
  "Black Rice": 190,
  "Bpt Rice": 68,
  "Broken Rice": 50,
  "Brown Rice": 80,
  "Hand Pounded Rice": 96,
  "Idli Rice": 85,
  "Karungkuruvai Rice": 115,
  "Kitchili Samba Boiled Rice": 92,
  "Kitchili Samba Rice": 88,
  "Mapillai Samba Rice": 105,
  "Matta Rice": 82,
  "Parboiled Rice": 75,
  "Ponni Rice Boiled": 78,
  "Ponni Rice Raw": 80,
  "Poongar Rice": 98,
  "Red Poha": 88,
  "Red Rice": 95,
  "Rice Flour": 75,
  "Seeraga Samba Rice": 110,
  "Chia Seed (Whole)": 280,
  "Flax Seed (Whole)": 110,
  "Groundnuts": 95,
  "Sesame Seed Black (Whole)": 135,
  "Sesame Seed White (Whole)": 125,
  "Ajwain (Powder)": 265,
  "Ajwain (Whole)": 255,
  "Bay Leaf": 110,
  "Biryani Masala": 1950,
  "Black Cumin Kala Jeera": 450,
  "Black Pepper (Powder)": 980,
  "Black Pepper (Whole)": 950,
  "Cardamom (Powder)": 2400,
  "Cardamom (Whole)": 1950,
  "Chaat Masala": 340,
  "Cinnamon (Powder)": 460,
  "Cinnamon (Whole)": 410,
  "Clove (Powder)": 1300,
  "Clove (Whole)": 1180,
  "Coriander (Powder)": 290,
  "Coriander (Whole)": 240,
  "Cumin (Powder)": 385,
  "Cumin (Whole)": 365,
  "Dry Red Chilli": 320,
  "Fennel (Powder)": 310,
  "Fennel (Whole)": 290,
  "Fenugreek (Powder)": 100,
  "Fenugreek (Whole)": 90,
  "Garam Masala": 340,
  "Hing Asafoetida": 935,
  "Mustard (Powder)": 130,
  "Mustard (Whole)": 120,
  "Rasam (Powder)": 310,
  "Star Anise": 420,
  "Turmeric": 210,
  "Whole Red Chillies": 320,
  "Brown Sugar": 85,
  "Coconut Sugar": 290,
  "Honey": 390,
  "Jaggery (Powder)": 88,
  "Jaggery (Solid)": 82,
  "Palm Jaggery": 180,
  "Stevia Leaf (Powder)": 650,
  "CTC Tea": 315,
  "Green Tea Leaf": 770,
  "Organic Coffee Arabica": 620,
  "Organic Coffee Robusta": 560,
  "Sambar Powder": 165

}

APPROVED_SKU_LIST = {item.strip().lower() for item in APPROVED_SKU_LIST_RAW}
NORMALIZED_PRICE_DICT = {k.strip().lower(): v for k, v in PRICE_DICT.items()}

# --- Streamlit UI Setup ---
st.set_page_config(page_title="🧬 Lifecode Recipe Generator", layout="centered")
# --- Custom CSS ---
try:
    with open(CSS_FILE, encoding="utf-8") as f:
     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"❌ CSS file not found at '{CSS_FILE}'.")
except Exception as e:
    st.error(f"❌ Error loading CSS: {e}")

# --- Utilities ---
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

# --- Logo and Header ---
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
if os.path.exists(logo_path):
    logo_b64 = get_base64_image(logo_path)
    st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{logo_b64}'></div>", unsafe_allow_html=True)
st.markdown("""
    <h1>🍛 Lifecode Recipe Generator</h1>
    <p>From Insight to Foresight: Traditional Tamil recipes with modern precision</p>
</div>
""", unsafe_allow_html=True)



# --- Gemini API Key Entry ---
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

with st.sidebar:
    st.markdown("### 🔐 Gemini API Key")
    st.session_state.gemini_api_key = st.text_input(
        "Enter your Gemini API key:",
        type="password",
        value=st.session_state.gemini_api_key,
        placeholder="Your_Key",
    )
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar.")

def load_memory():
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Recipe_Name",
            "Standard_Portion_Assumed_(Per_Person)",
            "Ingredients_(with_unit_quantity)",
            "Organic_Grocery_Required_(Per_Person)",
            "Grocery_Didn’t_Match_(if_any)",
            "Suitable_Accompaniment_(if_any)",
            "Total_Cost_(₹_Per_Person)",
            "Response"
        ])

    # Always regenerate normalized lookup key
    df["__Recipe_Lookup_Key"] = df["Recipe_Name"].fillna("").str.strip().str.lower()
    return df


def ask_gemini_for_recipe(recipe_name):
    if not st.session_state.get("gemini_api_key"):
        st.error("❌ Gemini API key is missing.")
        return "API key not provided."

    genai.configure(api_key=st.session_state.gemini_api_key, transport="rest")

    prompt = f"""
You are a 60+ year Chettinad culinary expert. Provide a traditional Tamil recipe for '{recipe_name}' in the following format:
Return the ingredients as a **JSON array** with keys: `name`, `quantity`, and `purpose`.
Then provide rest of the recipe as:

🍃 Recipe Name: <name>
🍽️ Standard Portion Assumed (Per Person): <details>
🌿 Organic Grocery Required (Per Person): <list>
🥗 Suitable Accompaniment (if any): <optional>
🧾 Preparation Steps: <steps>
"""

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return "Gemini failed to generate a recipe."

def parse_gemini_response(response_text, recipe_name):
    json_part = re.search(r"\[.*?\]", response_text, re.DOTALL)
    ingredients_json = []
    if json_part:
        try:
            ingredients_json = json.loads(json_part.group())
        except json.JSONDecodeError:
            st.error("❌ Failed to parse ingredients JSON from Gemini.")

    sections = {
        "Recipe_Name": recipe_name.strip().title(),
        "Standard_Portion_Assumed_(Per_Person)": "",
        "Ingredients_(with_unit_quantity)": "",
        "Organic_Grocery_Required_(Per_Person)": "",
        "Suitable_Accompaniment_(if_any)": "",
        "Response": "",  # Will hold multi-line Preparation Steps
        "__parsed_json_ingredients": ingredients_json
    }

    # Format ingredients as a list
    sections["Ingredients_(with_unit_quantity)"] = "\n".join(
        f"- {i['quantity']} {i['name']} ({i.get('purpose', '')})" for i in ingredients_json
    )

    # Map for single-line fields
    label_map = {
        "standard portion": "Standard_Portion_Assumed_(Per_Person)",
        "organic grocery": "Organic_Grocery_Required_(Per_Person)",
        "suitable accompaniment": "Suitable_Accompaniment_(if_any)"
    }

    # Parse single-line metadata
    for line in response_text.splitlines():
        for label, key in label_map.items():
            if label in line.lower():
                sections[key] = line.split(":", 1)[-1].strip()

    # ✅ Extract multi-line preparation steps block
    prep_match = re.search(r"🧾 Preparation Steps:\s*(.+?)(\n[#@:🔸🌿🍛🍽️🌿🌾🧂🥣🥘🍚🧾]|$)", response_text, re.DOTALL)
    if prep_match:
        steps = prep_match.group(1).strip()
        sections["Response"] = steps
    else:
        sections["Response"] = "Gemini failed to generate preparation steps."

    return sections


def compute_cost(ingredients_json):
    unmatched = []
    total_cost = 0.0

    for item in ingredients_json:
        raw_name = item["name"].strip().lower()

        # Use fuzzy matching to get closest SKU
        match = difflib.get_close_matches(raw_name, APPROVED_SKU_LIST, n=1, cutoff=0.6)
        if match:
            matched_sku = match[0]
            unit_price = NORMALIZED_PRICE_DICT.get(matched_sku, 0)
            total_cost += unit_price / 10  # crude estimate per person
            print(f"[MATCHED] {raw_name} → {matched_sku} → ₹{unit_price}")
        else:
            unmatched.append(raw_name)
            print(f"[UNMATCHED] {raw_name}")

    return total_cost, unmatched



# --- Chat Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# --- Main Chat Flow ---
if user_input := st.chat_input("Which Tamil recipe would you like today?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching Lifecode Chef's memory..."):
            df = load_memory()
            # Clean recipe names in dataframe
            df["__Recipe_Lookup_Key"] = df["Recipe_Name"].fillna("").str.strip().str.lower()
            user_query = user_input.strip().lower()

            match_row = df[df["__Recipe_Lookup_Key"] == user_query]


            if not match_row.empty:
                row = match_row.iloc[0]
                response_md = f"""
<p style='color:#007bff; font-style:italic;'>📒 Lifecode Chef remembered this one!</p>
## {row['Recipe_Name']}

### Portion Details
{row['Standard_Portion_Assumed_(Per_Person)']}

### Ingredients
{row['Ingredients_(with_unit_quantity)']}

### Preparation Steps
{row['Response']}

"""
                if str(row['Suitable_Accompaniment_(if_any)']).strip().lower() not in ['n/a', 'not applicable', '']:
                    response_md += f"### Suitable Accompaniment\n{row['Suitable_Accompaniment_(if_any)']}\n\n"
                response_md += f"### Estimated Cost\n{row['Total_Cost_(₹_Per_Person)']}\n\n"

                st.markdown(response_md, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response_md})
            else:
                with st.spinner("Recipe not found. Asking Gemini Chef..."):
                    raw_response = ask_gemini_for_recipe(user_input)
                    parsed_data = parse_gemini_response(raw_response, user_input)


                    cost, unmatched = compute_cost(parsed_data["__parsed_json_ingredients"])
                    parsed_data["Grocery_Didn’t_Match_(if_any)"] = ", ".join(unmatched)
                    parsed_data["Total_Cost_(₹_Per_Person)"] = f"₹ {round(cost, 2)}"
                    # Append to memory and save to Excel
                    df = pd.concat([df, pd.DataFrame([parsed_data])], ignore_index=True)
                    try:
                        df.drop(columns="__Recipe_Lookup_Key", errors="ignore").to_excel(EXCEL_FILE, index=False)
                    except Exception as e:
                        st.error(f"❌ Failed to save to Excel: {e}")


                    # Regenerate lookup key for consistency
                    # Normalize recipe name
                    normalized_recipe_name = user_input.strip().lower()



                    response_md = f"""
<p style='color:#ff8800; font-style:italic;'>🧠 Gemini Chef created this for you!</p>
## {parsed_data['Recipe_Name']}

### Portion Details
{parsed_data['Standard_Portion_Assumed_(Per_Person)']}

### Ingredients
{parsed_data['Ingredients_(with_unit_quantity)']}

### Preparation Steps
{parsed_data['Response']}

"""
                    if parsed_data["Suitable_Accompaniment_(if_any)"].lower() not in ["not applicable", "n/a", ""]:
                        response_md += f"### Suitable Accompaniment\n{parsed_data['Suitable_Accompaniment_(if_any)']}\n\n"
                    response_md += f"### Estimated Cost\n₹ {round(cost, 2)}\n\n"

                    st.markdown(response_md, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response_md})
