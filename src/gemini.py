import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def build_grounded_prompt(question, context):
    return f"""
You are StockSense AI, an explainable retail inventory decision copilot.

Use ONLY the information provided below.

Never invent:
- stock
- sales
- prices
- dates
- suppliers
- costs
- lead times
- purchase orders

If information is missing, clearly say:
"I don't have enough data to answer that."

RETAIL DATA:
{context}

STORE MANAGER QUESTION:
{question}

Answer clearly using:

Answer:
Evidence:
Recommended next step:
Data limitation:
"""


def ask_stock_sense(question, context):
    client = get_client()

    if client is None:
        return {
            "success": False,
            "answer": "Gemini is not configured."
        }

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=build_grounded_prompt(question, context)
        )

        return {
            "success": True,
            "answer": response.text.strip(),
            "model": MODEL_NAME
        }

    except Exception as error:
        print("Gemini error:", error)

        return {
            "success": False,
            "answer": f"Gemini request failed: {error}"
        }