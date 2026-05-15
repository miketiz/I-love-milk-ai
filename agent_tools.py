"""Tools that the agent can call safely."""

from datetime import datetime
import os

from sheets_client import get_sheet
from rag_engine import RAGEngine


def validate_sale(menu: str, quantity: int, price: float) -> None:
    """Guardrails for sale input."""
    if not menu or not str(menu).strip():
        raise ValueError("ชื่อเมนูห้ามว่าง")
    if quantity <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")
    if price <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")


def log_sale(menu: str, quantity: int, price: float) -> dict:
    """Append one sale row to Google Sheets and return summary."""
    validate_sale(menu, quantity, price)
    total = round(quantity * price, 2)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet = get_sheet()
    sheet.append_row([timestamp, menu, quantity, price, total])

    return {
        "status": "success",
        "menu": menu,
        "quantity": quantity,
        "price": price,
        "total": total,
        "timestamp": timestamp,
    }


def answer_question(question: str) -> dict:
    """Search knowledge base and return relevant answer context."""
    try:
        import google.generativeai as genai
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing dependency: google-generativeai"
        ) from exc

    kb_path = os.path.join(os.path.dirname(__file__), "knowledge", "milklab_kb.txt")
    if not os.path.exists(kb_path):
        return {
            "status": "error",
            "error": "ไม่พบฐานความรู้",
        }

    rag = RAGEngine(kb_path)
    results = rag.search(question, top_k=3)
    
    if not results:
        return {
            "status": "no_context",
            "error": "ไม่พบข้อมูลที่เกี่ยวข้อง",
        }

    context = "\n".join(results)
    return {
        "status": "success",
        "context": context,
        "num_results": len(results),
    }


TOOLS = {
    "log_sale": log_sale,
    "answer_question": answer_question,
}
