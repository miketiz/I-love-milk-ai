"""Morning report: summarize today's sales from Google Sheets and send to Telegram."""

import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv
import requests
import html

try:
    from sheets_client import get_sheet
except Exception as exc:
    print("Missing sheets_client or dependency:", exc)
    raise


def summarize_today(sheet):
    today_str = date.today().isoformat()  # YYYY-MM-DD
    rows = sheet.get_all_values()

    total = 0.0
    count = 0
    last_row = None

    for r in rows:
        if not r:
            continue
        # Expect: [timestamp, menu, quantity, price, total]
        ts = r[0]
        try:
            if ts.startswith(today_str):
                # parse total from column 5 (index 4)
                t = float(r[4]) if len(r) > 4 and r[4] != "" else 0.0
                total += t
                count += 1
                last_row = r
        except Exception:
            # ignore parse errors per-row
            continue

    return {
        "date": today_str,
        "count": count,
        "total": round(total, 2),
        "last_row": last_row,
    }


def send_telegram(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=payload, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print("Failed to send Telegram message:", e)
        try:
            print("Response:", resp.text)
        except Exception:
            pass
        return False


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    load_dotenv(dotenv_path=".env", override=True)

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in env")
        sys.exit(2)

    try:
        sheet = get_sheet()
    except Exception as e:
        print("Failed to get Google Sheet:", e)
        sys.exit(2)

    summary = summarize_today(sheet)

    # Format message using HTML for nicer appearance
    def esc(s: str) -> str:
        return html.escape(str(s))

    header = f"<b>Morning Report — {esc(summary['date'])}</b>"
    stats = f"Rows: <b>{summary['count']}</b>\nTotal: <b>{summary['total']:.2f} ฿</b>"

    body = header + "\n" + stats

    if summary.get("last_row"):
        lr = summary["last_row"]
        # Make a compact preformatted line for the last row
        # Join columns with tab-like spacing
        pre = " | ".join(esc(c) for c in lr)
        body += "\n\n<pre>Last: " + pre + "</pre>"

    print(body)

    ok = send_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, body)
    if not ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
