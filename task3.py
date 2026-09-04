import os
import math
from google import genai

# Pass your copied API key directly inside the quotes below
API_KEY = "YOUR_API_KEY_HERE"

# Connect to the Google GenAI service
client = genai.Client(api_key=API_KEY)

print("=== Task 3: Simple AI Agent ===")

# 1. Define the task
task = "Calculate the square root of 144, add 10 to it, and then multiply the result by 2."
print(f"Assigned Task: {task}\n")

print("--- Step 1: Planning ---")
# Ask the LLM to break the task down into exact, distinct steps
planning_prompt = (
    f"You are an AI Agent. Break down the following task into a bulleted list of distinct mathematical operations "
    f"required to solve it. Keep it brief.\nTask: {task}"
)

response_plan = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=planning_prompt,
)
print(response_plan.text)

print("--- Step 2: Execution ---")
# The Python backend executes the hard logic based on the task
# Step A: Square root of 144
step1_res = math.sqrt(144)
print(f"Executing Step 1 (Square root of 144): {step1_res}")

# Step B: Add 10
step2_res = step1_res + 10
print(f"Executing Step 2 (Add 10): {step2_res}")

# Step C: Multiply by 2
final_numeric_res = step2_res * 2
print(f"Executing Step 3 (Multiply by 2): {final_numeric_res}\n")

print("--- Step 3: Final Output Generation ---")
# Feed the raw work back to the LLM to format the final clean response
final_prompt = (
    f"Formulate a final, polished response for the user explaining the result. "
    f"The original task was: '{task}'. The math execution yielded a final answer of {final_numeric_res}. "
    f"Confirm the step-by-step results clearly."
)

response_final = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=final_prompt,
)
print(response_final.text)

print("=== Agent Task Complete ===")

# Final verified version