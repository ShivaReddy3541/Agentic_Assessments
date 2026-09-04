import os
from google import genai

# Pass your copied API key directly inside the quotes below
API_KEY = "YOUR_API_KEY_HERE"

# Connect to the Google GenAI service
client = genai.Client(api_key=API_KEY)

print("=== Task 1: Basic LLM Workflow ===")

# 1. Accept user input
user_input = input("Enter your prompt for the AI: ")

print("\nSending request to Gemini...")

# 2. Generate a response using the recommended fast model
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=user_input,
)

# 3. Display the final output
print("\n=== AI Response ===")
print(response.text)

# Final verified version