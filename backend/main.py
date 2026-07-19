from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import os

# Load API key from .env
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Model
class CodeRequest(BaseModel):
    language: str
    code: str


# Home Route
@app.get("/")
def home():
    return {"message": "AI Code Review Assistant Backend Running!"}


# List Available Models
@app.get("/models")
def list_models():
    models = []

    for model in client.models.list():
        models.append(model.name)

    return models


# Review Endpoint
@app.post("/review")
def review_code(request: CodeRequest):

    prompt = f"""
You are a senior software engineer reviewing code.

Review the following {request.language} code.

Rules:
1. If the code has no major issues, clearly say "No major issues found."
2. Do NOT suggest unnecessary improvements like type hints or docstrings for very simple programs.
3. Focus only on:
   - Bugs
   - Logic errors
   - Performance improvements
   - Security issues
   - Readability (only if it significantly affects understanding)
4. Keep the review concise.
5. If the code is already good, appreciate it instead of inventing improvements.

Return the review in this format:

⭐ Overall Rating: x/10

🐞 Bugs
- ...

⚡ Optimizations
- ...

🧹 Best Practices
- ...

💡 Suggestions
- ...

Code:

{request.code}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt,
        )

        return {
            "review": response.text
        }

    except Exception as e:
        return {
            "error": str(e)
        }
