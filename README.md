# email2json

## Project Setup

This project assumes that you have already installed llama3.2 locally, and also uv package manager

### Install dependencies

uv sync

## Initial Test

### Run extract.py

uv run src/extract.py

We got the below output:

{
  "sender_name": "Priya Raman",
  "sender_email": "priya.raman@northwind.co",
  "category": "meeting",
  "urgency": "high",
  "meeting_requested": true,
  "deadline": null,
  "action_items": [
    "Sai"
  ]
}

### Observations

- we got the deadline as null instead of 2026-08-14

- we got the wrong action_items

### Suggested solution

I know, you might be thinking to change the system prompt. But, let's try to resolve this in a different way

