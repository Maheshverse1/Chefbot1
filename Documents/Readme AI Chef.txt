Here’s a simple, step-by-step guide to get you started with the ChefBot — our AI-based recipe memory system that writes and remembers recipes like a seasoned South Indian chef.
STEP 1: INSTALL REQUIRED SOFTWARE

    Install Python (if not already installed)

        Visit: https://www.python.org/downloads/

        Download the latest version (Python 3.10 or above)

        During installation, make sure to tick the checkbox:
        "Add Python to PATH"

    Open Command Prompt (on Windows) or Terminal (on Mac/Linux)

    Install required libraries by typing this:
    pip install streamlit openai pandas

STEP 2: GET YOUR OPENAI API KEY

    Go to: https://platform.openai.com/account/api-keys

    Click "Create new secret key"

    Copy the key (example: sk-abc123...)

    Save it somewhere safe (like Notepad)

STEP 3: DOWNLOAD THE APP FILES

    You will receive a folder named "chefbot_streamlit_app" (from Mahesh).

    This folder contains:

        app.py --> Main app file

        data/Recipebase.xlsx --> Recipe memory (auto-generated if missing)

        scripts/ --> Optional helper scripts

STEP 4: RUN THE APP

    Open Command Prompt or Terminal

    Navigate to the folder you received:
    Example:
    cd C:\Users\YourName\Downloads\chefbot_streamlit_app
    (Replace this path with your actual folder location)

    Run the Streamlit app:
    streamlit run app.py

    It will open a local webpage in your browser (usually at http://localhost:8501)

STEP 5: USE THE CHEFBOT

    Paste your OpenAI API key in the box when prompted.

    Enter the dish name (example: Kozhi Milagu Rasam)

    Click the "Get the Recipe" button

The ChefBot will:

    First check if the recipe already exists in Recipebase.xlsx

    If found, it shows the saved version (unchanged)

    If not found, it asks ChatGPT to generate the recipe

    Then saves it to Excel and shows you the result

WHAT THIS SOLVES

    You will now get the SAME ingredients, quantities, and prices every time

    Recipes once generated are "locked" and saved

    You don’t have to upload or manage RAG files manually