import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # loads .env file
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in .env")

client = OpenAI(api_key=api_key)  # pass api_key explicitly
MODEL_NAME = "gpt-4o-mini"

def ask_ai(question, action="General"):
    prompt = f"""
You are a helpful travel guide. The user asked: "{question}".
Action: {action}

Return JSON ONLY. Use this structure:

{{
  "description": "Short travel info",
  "landmarks": ["Landmark1", "Landmark2"],
  "restaurants": ["Restaurant1", "Restaurant2"],
  "events": ["Event1", "Event2"],
  "city": "CityNameIfIdentified"
}}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400
    )
    return response.choices[0].message.content


def parse_ai_response(ai_response, action="General"):
    try:
        start = ai_response.find("{")
        end = ai_response.rfind("}") + 1
        if start != -1 and end != -1:
            data = json.loads(ai_response[start:end])
        else:
            data = {}

        description = data.get("description", "")
        city = data.get("city", "")

        if action in ["Landmarks", "General"]:
            items = data.get("landmarks", [])
        elif action == "Nearby Restaurants":
            items = data.get("restaurants", [])
        elif action == "Local Events":
            items = data.get("events", [])
        else:
            items = []

        return description, items, city

    except Exception as e:
        print("AI response parsing failed:", e)
        print("Raw AI response:", ai_response)
        return ai_response, [], ""



