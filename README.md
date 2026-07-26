# email2json

email2json converts messy emails into clean, validated JSON. A single Pydantic schema defines the output, forces the AI to return valid structured data, and rejects anything that doesn't fit, retrying until it does.

Measured field-by-field accuracy over 50 synthetic test emails.

## Project Setup

This project assumes that you have already installed llama3.2 locally, and also uv package manager

### Install dependencies

uv sync

## Initial Test

### Run extract.py

uv run src/extract.py

Output:

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

I know, you might be thinking to change the system prompt. But, let's try to resolve this in a different way.

Let's try to add some field validators to our schema and try to implement retry loop with the raised errors.

## Test - 2

Output:

{
  "sender_name": "Priya Raman",
  "sender_email": "priya.raman@northwind.co",
  "category": "meeting",
  "urgency": "high",
  "meeting_requested": true,
  "deadline": null,
  "action_items": [
    "Walk through the Q3 budget for 30 minutes on Thursday. Update headcount figures and sign off on vendor invoice."
  ]
}

## Now lets add accuracy.py which will give us the test results with field-by-field accuracy

Output:

Scored 46 docs

sender_name: 45/46
sender_email: 46/46
category: 36/46
urgency: 18/46
meeting_requested: 44/46
deadline: 45/46
action_items (F1): 0.475

Misses:
  sender_name 012: '' -> 'monitoring'
  category 006: 'other' -> 'meeting'
  category 015: 'other' -> 'personal'
  category 023: 'other' -> 'newsletter'
  category 028: 'meeting' -> 'newsletter'
  category 029: 'other' -> 'newsletter'
  category 033: 'newsletter' -> 'support'
  category 034: 'meeting' -> 'invoice'
  category 035: 'other' -> 'newsletter'
  category 042: 'other' -> 'invoice'
  category 048: 'other' -> 'support'
  urgency 001: 'medium' -> 'high'
  urgency 004: 'medium' -> 'high'
  urgency 006: 'medium' -> 'low'
  urgency 007: 'medium' -> 'low'
  urgency 008: 'medium' -> 'low'
  urgency 011: 'medium' -> 'low'
  urgency 012: 'medium' -> 'low'
  urgency 013: 'medium' -> 'low'
  urgency 014: 'medium' -> 'low'
  urgency 015: 'medium' -> 'high'
  urgency 017: 'medium' -> 'low'
  urgency 020: 'medium' -> 'high'
  urgency 021: 'medium' -> 'low'
  urgency 025: 'medium' -> 'low'
  urgency 028: 'medium' -> 'low'
  urgency 029: 'medium' -> 'low'
  urgency 030: 'medium' -> 'low'
  urgency 032: 'medium' -> 'high'
  urgency 034: 'medium' -> 'low'
  urgency 035: 'medium' -> 'high'
  urgency 037: 'medium' -> 'low'
  urgency 038: 'medium' -> 'low'
  urgency 040: 'medium' -> 'low'
  urgency 042: 'medium' -> 'low'
  urgency 044: 'medium' -> 'high'
  urgency 046: 'medium' -> 'low'
  urgency 048: 'medium' -> 'low'
  urgency 050: 'medium' -> 'high'
  meeting_requested 025: False -> True
  meeting_requested 045: False -> True
  deadline 038: None -> '2026-10-31'
  
All the fields looks good except urgency and category.

I tried altering the schema description, system prompt given to llama. But, still that gave the same result.

And by observing the tests, the llama3.2:2B model is good at extraction. But, when coming to the reasoning/judgement it is not able to produce accurate results.

So, Now, I wanted to connect a model which is bigger than llama3.2:2B and observe the result.

Output:

Scored 50 docs

sender_name: 49/50
sender_email: 50/50
category: 46/50
urgency: 45/50
meeting_requested: 50/50
deadline: 44/50
action_items (F1): 0.747

Misses:
  sender_name 012: '' -> 'Automated alert'
  category 013: 'personal' -> 'other'
  category 034: 'meeting' -> 'other'
  category 048: 'other' -> 'support'
  category 049: 'personal' -> 'other'
  urgency 006: 'medium' -> 'low'
  urgency 013: 'medium' -> 'low'
  urgency 025: 'medium' -> 'low'
  urgency 034: 'medium' -> 'low'
  urgency 038: 'medium' -> 'low'
  deadline 006: None -> '2026-05-02'
  deadline 014: None -> '2026-06-01'
  deadline 016: None -> '2026-03-11'
  deadline 019: None -> '2026-07-05'
  deadline 034: None -> '2026-04-22'
  deadline 038: None -> '2026-10-31'
  

The results look good. There's a lot of improvement on the reasoning/judgement based fields. But, we did notice a slight reduction in deadline field.

Field				Ollama (46 docs)	OpenAI (50 docs)	
sender_email		100%	100%	flat (extraction, saturated)
meeting_requested	95.7%	100%	↑
sender_name			97.8%	98%	flat
urgency				39.1%	90%	↑↑ huge
action_items		47.5%	74.7%	↑↑ huge
category			78.3%	92%	↑
deadline			97.8%	88%	↓ regressed!

And also, i don't judge the model on just this deadline field as I wasn't that clear on the deadline description in the Pydantic schema.

For the above tests, I used - gpt-4o-mini model.





