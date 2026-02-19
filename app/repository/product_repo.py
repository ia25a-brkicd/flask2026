from db import get_db

# ──────────────────────────────────────────────
# In-memory product catalogue (works without DB)
# ──────────────────────────────────────────────
PRODUCTS = [
    {
        "id": 1,
        "name": "Green Apple & Lemon mix",
        "price": 12.99,
        "category": "classic",
        "image": "images/Green Apple & Lemon mix.jpg",
        "short": "Erfrischende Mischung aus grünem Apfel und Zitrone.",
        "description": (
            "Diese handgefertigte Seife kombiniert den frischen Duft von grünem Apfel mit der spritzigen Note von Zitrone. "
            "Die natürlichen Inhaltsstoffe reinigen sanft und hinterlassen ein erfrischendes Gefühl auf der Haut. "
            "Perfekt für den täglichen Gebrauch und alle Hauttypen."
        ),
        "ingredients": "Olivenöl, Kokosöl, Sheabutter, Apfelextrakt, Zitronenöl, Vitamin E",
        "weight": "120g",
    },
    {
        "id": 2,
        "name": "Green Apple & Lemon & Vanille Mix",
        "price": 13.99,
        "category": "luxury",
        "image": "images/Green Apple & Lemon & Vanille Mix.jpg",
        "short": "Luxuriöse Kombination aus Apfel, Zitrone und Vanille.",
        "description": (
            "Eine exquisite Mischung aus grünem Apfel, Zitrone und cremiger Vanille. "
            "Diese Luxusseife verwöhnt die Sinne mit ihrem einzigartigen Duft und pflegt die Haut "
            "mit hochwertigen natürlichen Ölen. Handgefertigt mit Liebe zum Detail."
        ),
        "ingredients": "Sheabutter, Kokosöl, Apfelextrakt, Zitronenöl, Vanilleextrakt, Jojobaöl, Glycerin",
        "weight": "120g",
    },
    {
        "id": 3,
        "name": "Green Apple & Lemon with Stamp",
        "price": 14.99,
        "category": "luxury",
        "image": "images/Green Apple & Lemon with Stamp.jpg",
        "short": "Exklusive Seife mit dekorativem Stempel.",
        "description": (
            "Unsere Premium-Seife mit handgeprägtem Stempel vereint grünen Apfel und Zitrone. "
            "Jedes Stück ist ein Unikat und wird sorgfältig von Hand gefertigt. "
            "Die ideale Wahl für besondere Anlässe oder als besonderes Geschenk."
        ),
        "ingredients": "Bio-Honig, Haferflocken, Olivenöl, Kokosöl, Apfelextrakt, Zitronenöl, Bienenwachs, Vitamin E",
        "weight": "130g",
    },
    {
        "id": 4,
        "name": "Green Apple & Lemon",
        "price": 11.99,
        "category": "classic",
        "image": "images/Green Apple & Lemon.jpg",
        "short": "Die klassische Seife mit Apfel und Zitrone.",
        "description": (
            "Unsere klassische Green Apple & Lemon Seife bietet pure Frische zu einem unschlagbaren Preis. "
            "Die bewährte Rezeptur reinigt gründlich und hinterlässt einen belebenden Duft. "
            "Ideal für die ganze Familie."
        ),
        "ingredients": "Aktivkohle, Kokosöl, Teebaumöl, Sheabutter, Rizinusöl, Apfelextrakt, Zitronenöl",
        "weight": "110g",
    },
    {
        "id": 5,
        "name": "Green Apple & Vanille",
        "price": 12.49,
        "category": "classic",
        "image": "images/Green Apple & Vanille.jpg",
        "short": "Sanfte Kombination aus Apfel und Vanille.",
        "description": (
            "Die harmonische Verbindung von frischem grünem Apfel und süßer Vanille macht diese Seife zu etwas Besonderem. "
            "Sie pflegt die Haut sanft und hinterlässt einen angenehm warmen Duft. "
            "Perfekt für entspannende Momente."
        ),
        "ingredients": "Pfefferminzöl, Eukalyptusöl, Kokosöl, Olivenöl, Apfelextrakt, Vanilleextrakt, Menthol, Grüne Tonerde",
        "weight": "115g",
    },
    {
        "id": 6,
        "name": "Vanille & Lemon Mix",
        "price": 13.49,
        "category": "luxury",
        "image": "images/Green Apple & Lemon & Vanille Mix.jpg",
        "short": "Premium Vanille-Zitronen Seife mit extra Pflege.",
        "description": (
            "Unsere Luxus-Variante der Vanille & Lemon Mix Seife bietet intensive Pflege. "
            "Mit reichhaltigen Ölen und Butter verwöhnt sie die Haut und hinterlässt sie seidig weich. "
            "Der exotische Duft bringt Urlaubsgefühle in jede Dusche."
        ),
        "ingredients": "Kokosöl, Kokosmilch, Sheabutter, Kakaobutter, Zitronenöl, Vanilleextrakt, Vitamin E",
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