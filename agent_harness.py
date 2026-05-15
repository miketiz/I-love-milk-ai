"""Agent harness that converts Thai requests into validated tool calls."""

import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Missing dependency: google-generativeai. "
        "Install with: python -m pip install -r requirements.txt"
    ) from exc

from agent_tools import TOOLS

MODEL = "gemini-2.5-flash"
TRACE_FILE = "agent_trace.log"

SYSTEM_INSTRUCTION = """
คุณคือ Demi ผู้ช่วย AI ของร้าน MilkLab°.
หน้าที่ของคุณคือแปลงข้อความผู้ใช้เป็น JSON action เท่านั้น.

รูปแบบที่ถูกต้อง:
1. บันทึกยอดขาย: {"action": "log_sale", "args": {"menu": "...", "quantity": N, "price": N}}
2. ถามคำถาม: {"action": "answer_question", "args": {"question": "..."}}

ถ้าผู้ใช้ไม่ได้ถามข้อมูลหรือบันทึกยอดขาย ให้ตอบ:
{"action": "unknown", "args": {}}

ข้อบังคับ:
- ตอบ JSON เท่านั้น ห้ามมีข้อความอื่น
- สำหรับ log_sale: quantity ต้องเป็นจำนวนเต็ม, price เป็นตัวเลข
- สำหรับ answer_question: question เป็นข้อความแบบธรรมชาติภาษาไทย
- ถ้าคิดว่าเป็นคำสั่งบันทึกยอดขาย ให้ตอบ action log_sale
- ถ้าคิดว่าเป็นคำถามเกี่ยวกับเมนู ราคา เวลา ที่อยู่ หรือข้อมูลทั่วไป ให้ตอบ action answer_question
- ถ้าไม่แน่ใจ ให้ตอบ unknown แทนการอธิบาย
""".strip()

SALE_PATTERN = re.compile(
    r"(?P<menu>.+?)\s+(?P<quantity>\d+)\s*(?:แก้ว|ที่|ชิ้น|รายการ)?\s*(?:ราคา|ละ)?\s*(?P<price>\d+(?:\.\d+)?)\s*(?:บาท|฿)?$"
)


def write_trace(event: str, data: dict) -> None:
    with open(TRACE_FILE, "a", encoding="utf-8") as file:
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **data,
        }
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def ask_llm_for_action(user_input: str) -> str:
    response = genai.GenerativeModel(MODEL).generate_content(
        f"{SYSTEM_INSTRUCTION}\n\nคำสั่งผู้ใช้: {user_input}",
        generation_config={"response_mime_type": "application/json"},
    )
    return (response.text or "").strip()


def normalize_json_text(raw: str) -> str:
    """Normalize model output to a clean JSON object string."""
    text = (raw or "").strip()

    # Strip fenced blocks, e.g. ```json ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text).strip()

    # Fallback: extract the first JSON object from surrounding text.
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0).strip()
    return text


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


def run_agent(user_input: str) -> str:
    write_trace("user_input", {"message": user_input})

    # Fast path: if the user clearly typed a sale command, execute it directly.
    direct_action = fallback_sale_action(user_input)
    if direct_action:
        write_trace("direct_action", {"action": direct_action})
        action_data = direct_action
    else:
        raw = ask_llm_for_action(user_input)
        write_trace("llm_response", {"raw": raw})

        normalized = normalize_json_text(raw)

        try:
            action_data = json.loads(normalized)
        except json.JSONDecodeError:
            write_trace("parse_error", {"raw": raw, "normalized": normalized})
            return "❌ AI ตอบกลับไม่เป็น JSON ที่ถูกต้อง"

    action = action_data.get("action")
    args = action_data.get("args", {})

    if action == "unknown":
        write_trace("unknown_action", {"action": action, "args": args})
        return (
            "ผมช่วยสองอย่างครับ: (1) บันทึกยอดขาย หรือ (2) ตอบคำถามเกี่ยวกับเมนู\n"
            "ลองพิมพ์เช่น: 'บันทึกยอดขายลาเต้น้ำผึ้ง 5 แก้ว ราคา 65 บาท' "
            "หรือ 'ลาเต้มีน้ำตาลไหม'"
        )

    if action not in TOOLS:
        write_trace("unknown_action", {"action": action, "args": args})
        return f"⚠️ ไม่รู้จัก action: {action}"

    try:
        result = TOOLS[action](**args)
        write_trace("tool_result", {"action": action, "result": result})
        
        # Handle log_sale response
        if action == "log_sale":
            return (
                f"✅ บันทึกสำเร็จ\n"
                f"เมนู: {result['menu']}\n"
                f"จำนวน: {result['quantity']}\n"
                f"ราคา: {result['price']}\n"
                f"รวม: {result['total']} บาท"
            )
        
        # Handle answer_question response
        elif action == "answer_question":
            if result["status"] == "success":
                context = result["context"]
                # Call LLM to generate answer based on context
                qa_prompt = (
                    f"คำถาม: {user_input}\n\n"
                    f"ข้อมูลจากฐานความรู้:\n{context}\n\n"
                    f"โปรดตอบคำถามอย่างชัดเจนและเป็นมิตรตามข้อมูลข้างต้น"
                )
                qa_response = genai.GenerativeModel(MODEL).generate_content(qa_prompt)
                answer = (qa_response.text or "").strip()
                write_trace("qa_answer", {"question": user_input, "answer": answer})
                return answer
            elif result["status"] == "no_context":
                return (
                    "ขออภัย ผมไม่พบข้อมูลที่เกี่ยวข้องกับคำถามของคุณ\n"
                    "ลองถามเกี่ยวกับเมนู เวลาเปิด ราคา หรือวิธีสั่งอะไรแบบนี้"
                )
            else:
                return f"❌ ข้อผิดพลาด: {result.get('error', 'ไม่ทราบ')}"
        
        else:
            return f"✅ สำเร็จ: {result}"
            
    except (TypeError, ValueError) as exc:
        write_trace("tool_error", {"action": action, "args": args, "error": str(exc)})
        return f"❌ ข้อมูลไม่ถูกต้อง: {exc}"
    except Exception as exc:  # noqa: BLE001
        write_trace("system_error", {"action": action, "args": args, "error": str(exc)})
        return f"❌ ระบบขัดข้อง: {exc}"


def main() -> None:
    load_dotenv(dotenv_path=".env", override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env")

    genai.configure(api_key=api_key)

    print("Demi Agent พร้อมรับคำสั่ง (พิมพ์ 'exit' เพื่อออก)\n")
    while True:
        user_input = input("คุณ: ").strip()
        if user_input.lower() == "exit":
            print("Demi: แล้วพบกันใหม่")
            break
        if not user_input:
            continue
        print(f"Demi: {run_agent(user_input)}\n")


if __name__ == "__main__":
    main()
