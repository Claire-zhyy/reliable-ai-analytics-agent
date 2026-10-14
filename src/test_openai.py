from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-terra",
    input="Reply with exactly: API connection successful."
)

print(response.output_text)
