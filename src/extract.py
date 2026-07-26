import ollama
from schema import EmailExtraction
from pydantic import ValidationError
import os

MODEL = "llama3.2"
OPENAI_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You extract structured data from emails.
Read the email and fill in every field of the schema accurately.
Only use information present in the email. If a field is not mentioned, use null (or an empty list for action_items).
Do not invent names, addresses, dates, or tasks."""

def call_ollama(messages):
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        format=EmailExtraction.model_json_schema(),
        options={"temperature": 0},
    )
    return response["message"]["content"]

_openai_client = None

def call_openai(messages):
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        _openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    completion = _openai_client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=messages,
        response_format=EmailExtraction,
        temperature=0,
    )
    return completion.choices[0].message.content

BACKENDS = {
    "ollama": call_ollama,
    "openai": call_openai,
}

def extract(email_text, backend="ollama", max_attempts=3):
    call_model = BACKENDS[backend]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": email_text},
    ]

    last_error = None

    for attempt in range(1, max_attempts+1):
        raw = call_model(messages)

        try:
            return EmailExtraction.model_validate_json(raw), attempt
        except ValidationError as ve:
            last_error = ve
            print(f"  attempt {attempt} failed validation, retrying...")
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"That output was invalid:\n{ve}\n\nFix these problems and return corrected JSON.",
            })
    raise ValueError(f"Failed after {max_attempts} attempts. Last error:\n{last_error}")

def main():
    sample = """From: Priya Raman <priya.raman@northwind.co>
    Subject: Q3 budget review - need your numbers by Friday

    Hi Sai,

    Can we get 30 minutes on Thursday to walk through the Q3 budget?
    Before that, please send me the updated headcount figures and sign off
    on the vendor invoice. I need everything by 2026-08-14 at the latest.

    Thanks,
    Priya"""

    result, attempts = extract(sample, "openai")
    print(f"(took {attempts} attempt(s))")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()