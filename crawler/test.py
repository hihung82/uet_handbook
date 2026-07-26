import google.generativeai as genai
from config import Gemini_index_API

genai.configure(api_key=Gemini_index_API)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Hello")

print(response.text)