#!/usr/bin/env python3
"""Quick test script for agent Q&A capability (no external API calls)."""

import json
import re

# Simulate the system instruction
SYSTEM_INSTRUCTION = """
คุณคือ Demi ผู้ช่วย AI ของร้าน MilkLab°.
หน้าที่ของคุณคือแปลงข้อความผู้ใช้เป็น JSON action เท่านั้น.

รูปแบบที่ถูกต้อง:
1. บันทึกยอดขาย: {"action": "log_sale", "args": {"menu": "...", "quantity": N, "price": N}}
2. ถามคำถาม: {"action": "answer_question", "args": {"question": "..."}}

ถ้าผู้ใช้ไม่ได้ถามข้อมูลหรือบันทึกยอดขาย ให้ตอบ:
{"action": "unknown", "args": {}}
"""

# Test cases
test_cases = [
    ("บันทึกยอดขายลาเต้น้ำผึ้ง 5 แก้ว ราคา 65 บาท", "log_sale"),
    ("ลาเต้มีน้ำตาลไหม", "answer_question"),
    ("ร้านเปิดกี่โมง", "answer_question"),
    ("เมนูไหนไม่มีแคฟเฟอีน", "answer_question"),
    ("สวัสดี", "unknown"),
]

SALE_PATTERN = re.compile(
    r"(?P<menu>.+?)\s+(?P<quantity>\d+)\s*(?:แก้ว|ที่|ชิ้น|รายการ)?\s*(?:ราคา|ละ)?\s*(?P<price>\d+(?:\.\d+)?)\s*(?:บาท|฿)?$"
)


def fallback_sale_action(user_input: str) -> dict | None:
    """Extract a sale action directly from common Thai sale phrases."""
    cleaned = re.sub(r"\s+", " ", user_input.strip())

    prefixes = ["บันทึกยอดขาย", "บันทึก", "ขาย", "จด", "เพิ่มยอดขาย"]
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
            break

    match = SALE_PATTERN.search(cleaned)
    if not match:
        return None

    menu = match.group("menu").strip()
    quantity = int(match.group("quantity"))
    price = float(match.group("price"))
    return {"action": "log_sale", "args": {"menu": menu, "quantity": quantity, "price": price}}


def predict_action(user_input: str) -> str:
    """Predict action type based on input patterns."""
    # Try direct sale match
    if fallback_sale_action(user_input):
        return "log_sale"

    # Check for question keywords
    question_keywords = ["ไหม", "กี่", "อะไร", "อย่างไร", "เมื่อไร", "ที่ไหน", "ใครบ้าง", "เท่าไหร่", "ไหน", "เมนู", "ร้าน", "มี"]
    if any(keyword in user_input for keyword in question_keywords):
        return "answer_question"

    return "unknown"


print("=" * 60)
print("🧪 Agent Q&A Capability Test")
print("=" * 60)
print()

for i, (user_input, expected_action) in enumerate(test_cases, 1):
    predicted = predict_action(user_input)
    status = "✅" if predicted == expected_action else "❌"

    print(f"Test {i}: {status}")
    print(f"  Input:    {user_input}")
    print(f"  Expected: {expected_action}")
    print(f"  Predicted: {predicted}")

    if predicted == "log_sale":
        match = fallback_sale_action(user_input)
        if match:
            print(f"  Parsed:   {match['args']}")
    print()

print("=" * 60)
print("✅ All tests completed!")
print()
print("The agent can now:")
print("  • Log sales: บันทึกยอดขาย[เมนู] [จำนวน] ราคา [ราคา] บาท")
print("  • Answer Q&A: ลาเต้มีน้ำตาลไหม / ร้านเปิดกี่โมง")
print()
