from db import get_db

# ──────────────────────────────────────────────
# In-memory product catalogue (works without DB)
# ──────────────────────────────────────────────
PRODUCTS = [
    {
        "id": 1,
        "name": "Lavender Dream Soap",
        "price": 12.99,
        "category": "classic",
        "image": "styles/image/soaps.jpg",
        "short": "Handcrafted with real lavender flowers and essential oils.",
        "description": (
            "Our Lavender Dream Soap is handcrafted and contains authentic lavender flowers "
            "and essential oils from Provence. The soothing aroma relaxes body and mind with every wash. "
            "Suitable for all skin types, especially sensitive skin. Vegan and cruelty-free."
        ),
        "ingredients": "Olive Oil, Coconut Oil, Shea Butter, Lavender Oil, Lavender Flowers, Vitamin E",
        "weight": "120g",
    },
    {
        "id": 2,
        "name": "Rose Garden Soap",
        "price": 13.99,
        "category": "luxury",
        "image": "styles/image/soaps.jpg",
        "short": "Infused with rose petals and natural moisturizers.",
        "description": (
            "Rose Garden Soap combines the elegance of rose petals with natural moisturizers. "
            "Each bar is lovingly handcrafted and decorated with authentic rose flowers. "
            "Pampers your skin to silky softness and leaves behind a delicate rose fragrance."
        ),
        "ingredients": "Shea Butter, Coconut Oil, Rose Oil, Rose Petals, Jojoba Oil, Glycerin",
        "weight": "120g",
    },
    {
        "id": 3,
        "name": "Honey Glow Soap",
        "price": 12.49,
        "category": "classic",
        "image": "styles/image/soaps.jpg",
        "short": "Made with organic honey and oatmeal.",
        "description": (
            "Our Honey Glow Soap combines organic honey with fine oatmeal for a gentle exfoliating experience. "
            "The honey provides intensive moisture, while the oatmeal removes dead skin cells. "
            "Ideal for dry and sensitive skin."
        ),
        "ingredients": "Organic Honey, Oatmeal, Olive Oil, Coconut Oil, Beeswax, Vitamin E",
        "weight": "130g",
    },
    {
        "id": 4,
        "name": "Charcoal Detox Soap",
        "price": 14.99,
        "category": "classic",
        "image": "styles/image/soaps.jpg",
        "short": "Deep cleansing with activated charcoal.",
        "description": (
            "Charcoal Detox Soap deeply cleanses skin with activated charcoal. "
            "It draws out impurities and toxins from pores, leaving skin refreshed and clear. "
            "Especially suitable for oily and blemish-prone skin."
        ),
        "ingredients": "Activated Charcoal, Coconut Oil, Tea Tree Oil, Shea Butter, Castor Oil",
        "weight": "110g",
    },
    {
        "id": 5,
        "name": "Mint Fresh Soap",
        "price": 11.99,
        "category": "classic",
        "image": "styles/image/soaps.jpg",
        "short": "Refreshing peppermint for an energizing wash.",
        "description": (
            "Mint Fresh Soap invigorates with cool peppermint and eucalyptus. "
            "Perfect as a morning refresher – the mint scent awakens your senses and leaves "
            "a pleasantly tingling sensation on your skin."
        ),
        "ingredients": "Peppermint Oil, Eucalyptus Oil, Coconut Oil, Olive Oil, Menthol, Green Clay",
        "weight": "115g",
    },
    {
        "id": 6,
        "name": "Coconut Bliss Soap",
        "price": 13.49,
        "category": "luxury",
        "image": "styles/image/soaps.jpg",
        "short": "Tropical coconut for silky smooth skin.",
        "description": (
            "Coconut Bliss Soap transports you to the tropics. Rich coconut oil and coconut milk "
            "pamper your skin to silky softness. The exotic fragrance brings vacation vibes to every wash."
        ),
        "ingredients": "Coconut Oil, Coconut Milk, Shea Butter, Cocoa Butter, Vitamin E",
        "weight": "125g",
    },
]


def get_all_products_local():
    """Return all products from in-memory catalogue."""
    return PRODUCTS


def get_product_by_id(product_id):
    """Return a single product by its ID, or None."""
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return None


def search_products(query):
    """Search products by name (case-insensitive)."""
    q = query.lower()
    return [p for p in PRODUCTS if q in p["name"].lower() or q in p.get("category", "").lower()]


def get_products_by_category(category):
    """Return products filtered by category."""
    return [p for p in PRODUCTS if p["category"] == category]


# ──────────────────────────────────────────────
# DB-backed functions (kept for compatibility)
# ──────────────────────────────────────────────
def add_product(name, price):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (name, price))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()


def get_all_products():
    """Try DB first, fall back to in-memory catalogue."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        cur.close()
        return products
    except Exception:
        return [(p["id"], p["name"], p["price"]) for p in PRODUCTS]