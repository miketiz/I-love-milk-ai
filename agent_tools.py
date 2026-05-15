"""Tools that the agent can call safely."""

from datetime import datetime

from sheets_client import get_sheet


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


TOOLS = {
    "log_sale": log_sale,
}
