import os
from google import genai

# Pass your copied API key directly inside the quotes below
API_KEY = "YOUR_API_KEY_HERE"

# Connect to the Google GenAI service
client = genai.Client(api_key=API_KEY)

print("=== Task 2: Prompt Chaining Workflow ===")

# Get the initial topic from the user
topic = input("Enter a topic (e.g., Quantum Computing, Photosynthesis): ")

print("\n--- Step 1: Generating Summary ---")
summary_prompt = f"Provide a brief, 3-sentence summary explaining the topic: {topic}"
response1 = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=summary_prompt,
)
summary = response1.text
print(summary)

print("\n--- Step 2: Extracting Key Points ---")
# We pass the summary from Step 1 into this new prompt
points_prompt = f"Based ONLY on the following summary, extract 3 bulleted key points:\n\n{summary}"
response2 = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=points_prompt,
)
key_points = response2.text
print(key_points)

print("\n--- Step 3: Generating Questions ---")
# We pass the key points from Step 2 into this final prompt
questions_prompt = f"Based ONLY on the following key points, generate 3 thought-provoking questions:\n\n{key_points}"
response3 = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=questions_prompt,
)
questions = response3.text
print(questions)

print("\n=== Prompt Chaining Complete ===")

# Final verified version