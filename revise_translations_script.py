
# === SETUP GUIDE ===
# Set up google sheets API credentials + CREATE API KEY
# Install required packages:
# pip install openai gspread google-auth

import time
import openai
import gspread
import re
from google.oauth2.service_account import Credentials
from openai import OpenAIError

# === CONFIGURATION ===
openai.api_key = "sk-xxxxx"  # Replace with actual OpenAI key
GOOGLE_SHEETS_CREDS = "credentials.json" # Replace with credentials path
SHEET_NAME = "Traduction" # Pip = python app store/package manager, Openai → lets python connect to chat gpt, Gspread → lets python write in google sheets, Google-auth → lets python connect securely to google
TXT_OUTPUT_PATH = "/Users/shaden/Documents/LISA/revised_actions" #Need to create the folder and paste the path

# === PROMPT BUILDER ===
def build_prompt(english_action, french_action):
    return f"""
You will receive an English and French version of the same classroom action.
The French version includes expert edits. Your task is to revise the English version to incorporate these updates across the following sections:
– Title  
– Short description  
– Long description  
– Breakdown by subject 

Follow these formatting rules (Notion-compatible):
– Use manual hyphens (`-`) for bullet points  
– Use bolded numbered steps (`**1: text**`) for key action steps  
– Add zero-width spaces between each section to preserve line spacing when copy-pasting  
– In subject-specific examples, replace “French” with “Main language and literature”  

Translation guidelines:
– Prioritize clarity and instructional intent over literal translation.
– Render the tone of the French source into natural, culturally appropriate English for international educators.
– Use short, active sentences (subject–verb–object)  
– Simplify dense or abstract phrases into accessible English  
– Use culturally relevant classroom terminology (e.g., “implement” instead of “put in place”)  

Guiding principles:
Meaning over form
Didactic clarity
Cognitive load management
Contextual adaptation

ENGLISH VERSION:
{english_action}

FRENCH VERSION:
{french_action}

NOW RETURN ONLY THE REVISED ENGLISH VERSION IN CODE FORMAT, WITH THE FOLLOWING HEADERS:
**Title:**
**Short description:**
**Long description:**
**Breakdown by subject:**
"""

# === OPENAI CALL ===
def revise_action(english, french):
    prompt = build_prompt(english, french)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a translation assistant revising an English version based on expert-edited French input."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']

# === PARSE GPT OUTPUT INTO 4 FIELDS ===
def parse_revised_output(output_text):
    def extract_section(header, next_header=None):
        pattern = rf"\*\*{header}:\*\*\s*(.*?)\s*(?=\*\*{next_header}:\*\*|$)" if next_header else rf"\*\*{header}:\*\*\s*(.*)"
        match = re.search(pattern, output_text, re.DOTALL)
        return match.group(1).strip() if match else ""

    title = extract_section("Title", "Short description")
    short = extract_section("Short description", "Long description")
    long = extract_section("Long description", "Breakdown by subject")
    breakdown = extract_section("Breakdown by subject")
    return title, short, long, breakdown

# === MAIN FUNCTION ===
def process_sheet():
    # 🔐 Google Auth
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDS, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()

    #  Column Mapping
    headers = sheet.row_values(1)
    col_map = {name: idx + 1 for idx, name in enumerate(headers)} #added for col separation 

    # 🚀 Loop through rows
    for i, row in enumerate(data):
        row_number = i + 2  # 1-based indexing, +1 for header row
        if all(row.get(col) for col in ["Revised_EN_Title", "Revised_EN_Short", "Revised_EN_Long", "Revised_EN_Breakdown"]):
            continue  # Skip completed rows

        print(f"⏳ Processing row {row_number}...")

        english_action = f"{row['EN_Title']}\n\n{row['EN_Short']}\n\n{row['EN_Long']}\n\n{row['EN_Breakdown']}"
        french_action = f"{row['FR_Title']}\n\n{row['FR_Short']}\n\n{row['FR_Long']}\n\n{row['FR_Breakdown']}"

        try:
            revised_output = revise_action(english_action, french_action)
            title, short, long, breakdown = parse_revised_output(revised_output)

            sheet.update_cell(row_number, col_map["Revised_EN_Title"], title)
            sheet.update_cell(row_number, col_map["Revised_EN_Short"], short)
            sheet.update_cell(row_number, col_map["Revised_EN_Long"], long)
            sheet.update_cell(row_number, col_map["Revised_EN_Breakdown"], breakdown)
            print(f"✅ Written to sheet: row {row_number}")
            
             # 📝 Save full text to .txt file

            filename_title = row.get("EN_Title", f"row_{row_number}").strip().replace(" ", "_").replace("/", "-")
            filename = f"{TXT_OUTPUT_PATH}/{row_number:03d}_{filename_title[:50]}.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(revised_output)
            print(f"📝 Saved file: {filename}")
            
            time.sleep(1)  # 💤 reduce rate
            
        except OpenAIError as api_err:
            print(f"OpenAI error on row {row_number}: {api_err}")
            continue

        except Exception as e:
            print(f"⚠️  general Error on row {row_number}: {e}")
            continue

# === EXECUTE SCRIPT ===
if __name__ == "__main__":
    process_sheet()