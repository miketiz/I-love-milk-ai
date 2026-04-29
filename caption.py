"""Instagram caption generator for MilkLab cafe using Google Gemini AI."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv(dotenv_path=".env", override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_captions(menu_name: str, price: str) -> dict[str, str]:
    """Generate Instagram captions for a menu item.
    
    Args:
        menu_name: Name of the menu item (e.g., "Strawberry Milkshake")
        price: Price of the item (e.g., "$5.99")
        
    Returns:
        Dictionary with 3 caption styles: cute, minimal, and gen_z
    """
    prompt = f"""Generate 3 Instagram captions for a MilkLab cafe menu item. 
Item: {menu_name}
Price: {price}

Create exactly 3 captions in these styles:
1. cute - fun, playful, emoji-friendly
2. minimal - clean, short, sophisticated
3. gen_z - trendy, modern, slang-friendly

Format your response as:
CUTE: [caption]
MINIMAL: [caption]
GEN_Z: [caption]"""

    response = model.generate_content(prompt)
    text = response.text
    
    # Parse the response
    captions = {}
    for line in text.split('\n'):
        if line.startswith('CUTE:'):
            captions['cute'] = line.replace('CUTE:', '').strip()
        elif line.startswith('MINIMAL:'):
            captions['minimal'] = line.replace('MINIMAL:', '').strip()
        elif line.startswith('GEN_Z:'):
            captions['gen_z'] = line.replace('GEN_Z:', '').strip()
    
    return captions


if __name__ == "__main__":
    # Example usage
    print("Generating Instagram captions for Strawberry Milkshake...")
    captions = generate_captions("Strawberry Milkshake", "$5.99")
    
    print("\n✨ Generated Captions:")
    print(f"Cute: {captions.get('cute', 'N/A')}")
    print(f"Minimal: {captions.get('minimal', 'N/A')}")
    print(f"Gen Z: {captions.get('gen_z', 'N/A')}")
