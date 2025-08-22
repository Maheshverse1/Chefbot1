import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import re

# Setup
st.set_page_config(page_title="🔍 Gemini Recipe Debugger")
st.title("👨‍🍳 Lifecode Gemini Recipe Tester")

# File setup
EXCEL_FILE = "Recipebase_Debug.xlsx"
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

# Prompt Generator
def build_prompt(dish_name):
    approved_list = "\n".join([f"• {item}" for item in APPROVED_SKU_LIST])
    prices = "\n".join([f"• {k} – ₹{v}/kg or /L" for k, v in PRICE_DICT.items()])
    return f"""
You are a wise and experienced 60+ year old Chettinad chef working for a modern nutrition brand called Lifecode.
Use ONLY the approved ingredients and format shown.

====================
📦 APPROVED INGREDIENTS
====================
{approved_list}

====================
💰 INGREDIENT PRICES
====================
{prices}

====================
🎯 OUTPUT FORMAT
====================
1. Recipe Name (traditional Tamil): [Recipe]
2. Standard Portion Assumed (Per Person):
    • Yield – ___ g cooked
    • Calories – ___ kcal approx.
    • Quantity – ___
3. Ingredients (with unit quantity):
    • [Ingredient - quantity unit]
4. Organic Grocery Required (Per Person):
    • [Matched groceries]
5. Grocery Didn’t Match (if any):
    • [Unmatched] or • Not applicable
6. Suitable Accompaniment (if any): [Accompaniment]
7. Total Cost (₹ Per Person): ₹__
8. Response:
    1. Step-by-step instructions

Dish Name: {dish_name}
Only use g/ml. Never use cups, spoons, or other units.
"""

# Get user input
api_key = st.text_input("🔑 Gemini API Key", type="password")
dish_name = st.text_input("🍛 Enter Dish Name")

if api_key and dish_name:
    try:
        st.info("🔄 Initializing Gemini model...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = build_prompt(dish_name)
        st.success("✅ Gemini initialized. Sending prompt...")

        response = model.generate_content(prompt)
        output = response.text
        st.success("✅ Response received!")
        
        # Show raw output
        st.subheader("📤 Gemini Response")
        st.code(output, language="markdown")

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.warning("Please enter both your Gemini API key and a dish name to begin.")
