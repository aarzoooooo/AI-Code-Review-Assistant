from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
import os
import time
import random
import logging


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code-review")


class CodeRequest(BaseModel):
    language: str
    code: str


@app.get("/")
def home():
    return {
        "message": "AI Code Review Assistant Backend Running!"
    }


@app.get("/models")
def list_models():
    models = []
    for model in client.models.list():
        models.append(model.name)
    return models


MODEL_FALLBACK_CHAIN = [
    "gemini-3.6-flash",
]

MAX_RETRIES_PER_MODEL = 2
RETRYABLE_STATUS_CODES = {429, 503}


@app.post("/review")
def review_code(request: CodeRequest):

    prompt = f"""
You are a senior software engineer reviewing code.

Review the following {request.language} code.

Focus on:
- Bugs
- Logic errors
- Performance issues
- Security issues
- Important readability problems

Rules:
1. If there are no major issues, clearly say "No major issues found."
2. Do not suggest unnecessary improvements for simple programs.
3. Do not invent problems.
4. Keep the review concise.
5. Explain important issues clearly.

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

    last_error_message = "Unknown error."

    for model_name in MODEL_FALLBACK_CHAIN:

        for attempt in range(MAX_RETRIES_PER_MODEL):

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

                # Gemini can return a response with no text (e.g. blocked
                # by safety filters). Guard against that instead of
                # returning {"review": None}.
                if not response.text:
                    last_error_message = f"{model_name} returned an empty response (possibly filtered)."
                    logger.warning(last_error_message)
                    break  # try next model, no point retrying this one

                return {
                    "review": response.text
                }

            except genai_errors.APIError as e:
                status_code = getattr(e, "code", None)
                last_error_message = f"{model_name} APIError ({status_code}): {str(e)}"
                logger.warning(last_error_message)

                if status_code in RETRYABLE_STATUS_CODES:
                    is_last_attempt = attempt == MAX_RETRIES_PER_MODEL - 1
                    if not is_last_attempt:
                        wait_time = (2 ** attempt) + random.uniform(0, 0.5)
                        time.sleep(wait_time)
                else:
                    # Not retryable (bad request, bad key, etc.)
                    return {"error": str(e)}

            except Exception as e:
                # Catch-all: network errors, timeouts, SDK bugs, anything
                # not covered above. This is what was likely crashing the
                # request before and causing a raw 503 with no JSON body.
                last_error_message = f"{model_name} unexpected error: {str(e)}"
                logger.error(last_error_message)
                break  # don't retry unknown errors on this model, move to next

    return {
        "error": f"All models are currently unavailable. Last error: {last_error_message}"
    }
