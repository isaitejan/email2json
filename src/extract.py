import ollama
from schema import EmailExtraction

MODEL = "llama3.2"

SYSTEM_PROMPT = """You extract structured data from emails.
Read the email and fill in every field of the schema accurately.
Only use information present in the email. If a field is not mentioned, use null (or an empty list for action_items).
Do not invent names, addresses, dates, or tasks."""

def extract(email_text):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_text},
        ],
        format=EmailExtraction.model_json_schema(),
        options={"temperature": 0},
    )
    raw = response["message"]["content"]
    return EmailExtraction.model_validate_json(raw)

def main():
    sample = """From: Priya Raman <priya.raman@northwind.co>
    Subject: Q3 budget review - need your numbers by Friday

    Hi Sai,

    Can we get 30 minutes on Thursday to walk through the Q3 budget?
    Before that, please send me the updated headcount figures and sign off
    on the vendor invoice. I need everything by 2026-08-14 at the latest.

    Thanks,
    Priya"""

    result = extract(sample)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()