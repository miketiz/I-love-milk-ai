"""Sales logger for I Love Milk Cafe - logs sales to Google Sheets."""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

try:
    from sheets_client import get_sheet
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Missing sheets_client module. "
        "Make sure sheets_client.py exists in the project directory."
    ) from exc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")

if not GOOGLE_SHEETS_ID:
    raise ValueError("GOOGLE_SHEETS_ID not found in .env file")


def parse_sales_input(input_str: str) -> list[dict]:
    """Parse sales input in format: menu:quantity:price (can have multiple items).
    
    Args:
        input_str: Sales data in format "menu1:qty1:price1 menu2:qty2:price2"
                  Example: "Strawberry Milkshake:2:5.99 Mango Smoothie:1:4.99"
        
    Returns:
        List of dictionaries with menu, quantity, price, and total
        
    Raises:
        ValueError: If format is invalid
    """
    items = []
    entries = input_str.strip().split()
    
    for entry in entries:
        try:
            parts = entry.split(':')
            if len(parts) != 3:
                raise ValueError(f"Invalid format: {entry}. Expected: menu:quantity:price")
            
            menu_name = parts[0]
            quantity = int(parts[1])
            price = float(parts[2])
            total = quantity * price
            
            items.append({
                'menu': menu_name,
                'quantity': quantity,
                'price': price,
                'total': round(total, 2)
            })
        except (ValueError, IndexError) as e:
            raise ValueError(f"Error parsing '{entry}': {e}") from e
    
    return items


def calculate_grand_total(items: list[dict]) -> float:
    """Calculate total sum of all items.
    
    Args:
        items: List of item dictionaries with 'total' key
        
    Returns:
        Grand total amount
    """
    return round(sum(item['total'] for item in items), 2)


def log_sales_to_sheet(items: list[dict], grand_total: float):
    """Log sales to Google Sheets.
    
    Args:
        items: List of sold items
        grand_total: Total amount
    """
    sheet = get_sheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare row data - each item is a separate row
    for item in items:
        row_data = [
            timestamp,
            item['menu'],
            item['quantity'],
            item['price'],
            item['total']
        ]
        sheet.append_row(row_data)
    
    print(f"✅ Sales logged successfully at {timestamp}")


def main():
    """Main function to handle sales input and logging."""
    if len(sys.argv) < 2:
        print("Usage: python sales_logger.py 'menu1:qty1:price1 menu2:qty2:price2'")
        print("Example: python sales_logger.py 'Strawberry Milkshake:2:5.99 Mango Smoothie:1:4.99'")
        sys.exit(1)
    
    sales_input = sys.argv[1]
    
    try:
        # Parse input
        items = parse_sales_input(sales_input)
        
        # Calculate total
        grand_total = calculate_grand_total(items)
        
        # Display summary
        print("\n📊 Sales Summary:")
        print("-" * 50)
        for item in items:
            print(f"{item['menu']:30} {item['quantity']:>3} × ${item['price']:>6.2f} = ${item['total']:>7.2f}")
        print("-" * 50)
        print(f"{'TOTAL':30} {' ':>3} {' ':>8} ${grand_total:>7.2f}")
        print("-" * 50)
        
        # Log to Google Sheets
        log_sales_to_sheet(items, grand_total)
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
