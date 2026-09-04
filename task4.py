import os
from google import genai

# Pass your copied API key directly inside the quotes below
API_KEY = "YOUR_API_KEY_HERE"

# Connect to the Google GenAI service
client = genai.Client(api_key=API_KEY)

print("=== Task 4: Simple RAG System ===")

# 1. Ingestion: Load the document text
document_path = "knowledge.txt"
if not os.path.exists(document_path):
    print(f"Error: {document_path} not found! Please create it first.")
    exit()

with open(document_path, "r") as f:
    # Split the document into separate sentences/lines (chunks)
    chunks = [line.strip() for line in f.readlines() if line.strip()]

# 2. Get the user's question
question = input("Ask a question about the document: ")

print("\n--- Step 1: Retrieving Relevant Context ---")
# Basic keyword-matching retrieval mechanism
retrieved_chunks = []
words = question.lower().split()

for chunk in chunks:
    # If any word from the question matches words in the chunk, retrieve it
    if any(word in chunk.lower() for word in words if len(word) > 3):
        retrieved_chunks.append(chunk)

# Fallback: if no specific keywords match, use all text as context
if not retrieved_chunks:
    retrieved_chunks = chunks

context = "\n".join(retrieved_chunks)
print(f"Retrieved Context:\n{context}")

print("\n--- Step 2: Generating Answer via LLM ---")
# 3. Augment the prompt with the retrieved context
rag_prompt = f"""
You are a helpful assistant. Answer the user's question using ONLY the provided context below. 
If the answer cannot be found in the context, say "I cannot find the answer in the provided document."

Context:
{context}

Question: {question}
Answer:
"""

response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=rag_prompt,
)

print(response.text)
print("=== RAG Application Complete ===")

# Final verified version