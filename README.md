# Lisa-Action-Translator
Script to revise English classroom actions based on expert-edited French versions using GPT-4 and Google Sheets.
This script takes a French and English version of the same classroom action, revises the English version based on expert-edited French inputs, and saves the output into Google Sheets and `.txt` files.

## Dependencies
- openai
- gspread
- google-auth

## Install with:
pip install openai gspread google-auth

## Configuration
Set your `openai.api_key`, `GOOGLE_SHEETS_CREDS`, `SHEET_NAME`, and `TXT_OUTPUT_PATH` inside the script.


## 📁 Spreadsheet Columns

Your Google Sheet should contain these columns:
- EN_Title
- EN_Short
- EN_Long
- EN_Breakdown
- FR_Title
- FR_Short
- FR_Long
- FR_Breakdown
- Revised_EN_Title
- Revised_EN_Short
- Revised_EN_Long
- Revised_EN_Breakdown


## 📝 Output

Each revised action is:
- Written to four columns in the sheet
- Saved as a `.txt` file in the specified local folder

## ✍️ Author

Shaden — LearningPlanet Institute
