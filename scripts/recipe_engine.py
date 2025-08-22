import openai
import pandas as pd
import os

# Path to the Excel file (relative to this script's location)
EXCEL_FILE = os.path.join(os.path.dirname(__file__), '../data/Recipebase.xlsx')

def get_locked_recipe(dish_name):
    # Try to load existing Excel file or create new DataFrame if not found
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

    # Check if the recipe already exists in memory
    if dish_name in df["Recipe_Name"].values:
        result = df[df["Recipe_Name"] == dish_name]
        return result.to_string(index=False)

    # Prompt to get all 8 fields from GPT
    prompt = f"""You are a 60+ year Chettinad culinary and preventive health expert.

Dish Name: {dish_name}

Give the recipe in this exact 8-field format:
1. Recipe Name (traditional Tamil)
2. Standard Portion Assumed (Per Person)
3. Ingredients (with unit quantity in g/ml)
4. Organic Grocery Required (Per Person) – matched from approved SKU list only
5. Grocery Didn’t Match (if any)
6. Suitable Accompaniment (if any)
7. Total Cost (₹ Per Person, accurate to 2 decimals)
8. Response (Step-by-step preparation as a senior chef)

Ensure:
- All quantities must be fixed once generated
- Same ingredients and prices must be used every time
- No synonyms or variations allowed in the first 7 fields once it's saved"""

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )["choices"][0]["message"]["content"]

    print("\nGenerated Response:\n")
    print(response)

    # Split the 8 responses
    lines = response.strip().split("\n")
    values = [line.split(":", 1)[1].strip() if ":" in line else "" for line in lines[:8]]
    if len(values) < 8:
        values += [""] * (8 - len(values))

    # Add new row to Excel
    df.loc[len(df.index)] = values
    df.to_excel(EXCEL_FILE, index=False)

    return "\n".join([f"{col}: {val}" for col, val in zip(df.columns, values)])

if __name__ == "__main__":
    dish = input("Enter Dish Name: ")
    print(get_locked_recipe(dish))
