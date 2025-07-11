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
