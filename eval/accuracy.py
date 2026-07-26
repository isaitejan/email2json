from pathlib import Path
import sys
import json
from collections import Counter, defaultdict

EXACT_FIELDS = [
    "sender_name",
    "sender_email",
    "category",
    "urgency",
    "meeting_requested",
    "deadline",
]

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from extract import extract

TEST_SET = ROOT / "data" / "test_set.jsonl"

def load_test_set():
    rows = []
    with TEST_SET.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def norm(value):
    if isinstance(value, str):
        return value.strip().casefold()
    return value

def tokens(s):
    stop_words = {"the", "a", "an", "and", "or", "to", "of", "for", "on", "in",
                 "at", "by", "is", "be", "with", "your", "our", "you", "please"}

    s = s.lower().split()
    tmp = set()
    for item in s:
        if len(item.strip(".,:;!?()")) > 2 and item not in stop_words:
            tmp.add(item)
    return tmp

def find_items_match(a, b, threshold = 0.5):
    a = tokens(a)
    b = tokens(b)

    if len(a) == 0 and len(b) == 0:
        return True
    elif len(a) == 0 or len(b) == 0:
        return False

    intersection = a & b
    union = a | b

    jaccard = len(intersection) / len(union)

    if jaccard >= threshold:
        return True
    return False

def action_items_f1(expected, predicted):

    if not expected and not predicted:
        return 1.0

    if not expected or not predicted:
        return 0.0

    remaining = list(predicted)
    hits = 0
    for exp in expected:
        for i, pred in enumerate(remaining):
            if find_items_match(exp, pred):
                hits += 1
                remaining.pop(i)
                break

    precision = hits / len(predicted)
    recall = hits / len(expected)

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)

def main():
    rows = load_test_set()
    print(f"Loaded {len(rows)} rows\n")

    correct = Counter()
    misses = defaultdict(list)
    scored = 0
    f1_total = 0

    for row in rows:
        try:
            result, attempts = extract(row["email"], "openai")
        except Exception:
            continue  # hard failures handled properly in a later step

        scored += 1
        got = result.model_dump()
        expected = row["expected"]

        for field in EXACT_FIELDS:
            if norm(got[field]) == norm(expected[field]):
                correct[field] += 1
            else:
                misses[field].append((row["id"], expected[field], got[field]))

        f1_total += action_items_f1(expected["action_items"], got["action_items"])

    print(f"Scored {scored} docs\n")
    for field in EXACT_FIELDS:
        print(f"{field}: {correct[field]}/{scored}")

    print(f"action_items (F1): {f1_total / scored:.3f}")

    print("\nMisses:")
    for field in EXACT_FIELDS:
        for doc_id, exp, got_val in misses[field]:
            print(f"  {field} {doc_id}: {exp!r} -> {got_val!r}")

if __name__ == "__main__":
    main()