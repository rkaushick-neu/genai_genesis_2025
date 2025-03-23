import cohere
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(Path("./.env"))
print(os.getenv("COHERE_API_KEY"))

# Initialize Cohere client
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Generate a text response
response = co.generate(
    model="command",  # Use "command-r+" for better results (if available)
    prompt="Tell me a fun fact about space.",
    max_tokens=100
)

print(response.generations[0].text)