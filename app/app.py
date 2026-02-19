import db
import os
import re
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv # Lädt .env Datei
from mail import send_simple_message, send_order_confirmation
from repository.customer_repo import (
    add_customer_addres,
    add_customer_payment,
    add_login,
    verify_login,
    get_login_by_email,
    create_order,
    get_orders_by_login_id,
    get_orders_by_email,
    save_user_address,
    get_user_address
)
from services import math_service
from config import DevelopmentConfig, ProductionConfig
from flask_mail import Mail, Message
from repository import product_repo as db_repo

# Definieren einer Variable, die die aktuelle Datei zum Zentrum
# der Anwendung macht.
app = Flask(__name__)
app.secret_key = 'floravis-secret-key-2026'  # Für Session-Cookies

"""
Festlegen einer Route für die Homepage. Der String in den Klammernpip
bildet das URL-Muster ab, unter dem der folgende Code ausgeführt
werden soll.
z.B.
* @app.route('/')    -> http://127.0.0.1:5000/
* @app.route('/home') -> http://127.0.0.1:5000/home
"""

#-------------------------------
#Vorbereitungen
# 1. .env laden (macht lokal Variablen verfügbar, auf Render passiert nichts)
load_dotenv()


# 2. Config wählen
if os.environ.get('FLASK_ENV') == 'development':
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)

db.init_app(app)  # DB-Verbindung in Flask integrieren

# 3. Mail konfigurieren
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "465")),
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
)

mail = Mail(app)
#-------------------------------

# mock data
languages = [
    {"name": "Python", "creator": "Guido van Rossum", "year": 1991},
    {"name": "JavaScript", "creator": "Brendan Eich", "year": 1995},
    {"name": "Java", "creator": "James Gosling", "year": 1995},
    {"name": "C#", "creator": "Microsoft", "year": 2000},
    {"name": "Ruby", "creator": "Yukihiro Matsumoto", "year": 1995},
]

@app.route('/')
def home():
    print(math_service.add(1.0, 2.0))
    app.logger.info("Rendering home page")
    products = db_repo.get_all_products_local()[:6]  # Get first 6 products for carousel
    return render_template("home.html", products=products)

@app.route('/result/', defaults={'name': 'Guest'})
@app.route('/result/<name>')
def result(name) -> str:
    app.logger.info(f"Showing result for {name}")
    return render_template("result.html", name=name)

@app.route("/about_us")
def about_us() -> str:
    return render_template("about_us.html", languages=languages)

@app.route("/submit", methods=["POST"])
def submit():
    app.logger.info("Form submitted")
    name = request.form.get("name")
    return redirect(url_for("result", name=name))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    
    print("MAIL USER:", app.config.get("MAIL_USERNAME"))
    print("MAIL SERVER:", app.config.get("MAIL_SERVER"))

    if request.method == "POST":
        lastname = request.form.get("lastname")
        firstname = request.form.get("firstname")
        email = request.form.get("email")
        message = request.form.get("message")

        if not lastname or not firstname or not email or not message:
            return jsonify({"error": "Missing data"}), 400

        try:
            msg = Message(
                subject=f"New Contact Message from {firstname} {lastname}",
                recipients=[os.getenv("MAIL_RECIPIENT")],
                reply_to=email,
                body=(
                    f"First Name: {firstname}\n"
                    f"Last Name: {lastname}\n"
                    f"Email: {email}\n\n"
                    f"Message:\n{message}\n"
                ),
            )
            mail.send(msg)
            return jsonify({"success": True}), 200
        except Exception as e:
            app.logger.exception("Mail send failed")
            return jsonify({"error": "Mail failed"}), 500

    products = db_repo.get_all_products()
    return render_template("contact.html", products=products)




@app.route("/profil", methods=["GET", "POST"])
def profil():
    if request.method == "POST":
        app.logger.info("Form submitted")
        lastname = request.form.get("lastname")
        firstname = request.form.get("firstname")
        email = request.form.get("email")
        password = request.form.get("password")
        
        print("=== Profil Form Data ===")
        print(f"Name: {lastname}")
        print(f"Vorname: {firstname}")
        print(f"E-Mail: {email}")
        print(f"Passwort: {password}")
        print("========================")

        # HIER: "einloggen"
        session['user_id'] = email          # oder irgendeine ID
        session['user_name'] = firstname    # optional
        session['user_lastname'] = lastname

        add_login(email,firstname, lastname,password)# optional

        return redirect(url_for("home"))    # zurück zur Startseite

    adresse = session.get("adresse", {})
    versandadresse_same = session.get("versandadresse_same", False)
    versandadresse = adresse if versandadresse_same else session.get("versandadresse", {})
    user_profile = {
        "firstname": session.get("user_name", "-"),
        "lastname": session.get("user_lastname", "-"),
        "email": session.get("user_id", "-"),
        "password": "********" if session.get("user_id") else "-",
        "strasse": adresse.get("strasse", "-"),
        "plz": adresse.get("plz", "-"),
        "stadt": adresse.get("stadt", "-"),
        "land": adresse.get("land", "-"),
        "versand_strasse": versandadresse.get("strasse", "-"),
        "versand_plz": versandadresse.get("plz", "-"),
        "versand_stadt": versandadresse.get("stadt", "-"),
        "versand_land": versandadresse.get("land", "-"),
    }

    return render_template("profil.html", user_profile=user_profile)


@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = None
    if request.method == "POST":
        app.logger.info("Login submitted")
        email = request.form.get("email")
        password = request.form.get("password")

        print("=== Login Form Data ===")
        print(f"E-Mail: {email}")
        print(f"Passwort: {password}")
        print("=======================")

        # Überprüfe Login in der Datenbank
        is_valid, user_data = verify_login(email, password)

        if is_valid and user_data:
            # Login erfolgreich - user_data: (login_id, email, first_name, last_name, password)
            session['login_id'] = user_data[0]
            session['user_id'] = user_data[1]  # email
            session['user_name'] = user_data[2]  # first_name
            session['user_lastname'] = user_data[3]  # last_name

            # Lade Adressen aus der Datenbank (falls Tabelle existiert)
            try:
                billing_address = get_user_address(user_data[0], is_shipping=False)
                shipping_address = get_user_address(user_data[0], is_shipping=True)

                if billing_address:
                    session['adresse'] = billing_address
                if shipping_address:
                    session['versandadresse'] = shipping_address
            except Exception as e:
                print(f"⚠️ Konnte Adressen nicht laden: {e}")

            print(f"✅ Login erfolgreich für: {user_data[2]} {user_data[3]}")
            return redirect(url_for("profil"))
        else:
            # Login fehlgeschlagen
            print("❌ Login fehlgeschlagen - E-Mail oder Passwort falsch")
            error_message = "E-Mail oder Passwort falsch"

    return render_template("login.html", error_message=error_message)


@app.route("/orders")
def orders():
    # Prüfe ob User eingeloggt ist
    login_id = session.get('login_id')
    user_orders = []

    if login_id:
        # Lade Bestellungen aus der Datenbank
        user_orders = get_orders_by_login_id(login_id)
        print(f"📦 {len(user_orders)} Bestellungen geladen für User {login_id}")
    else:
        print("⚠️ User nicht eingeloggt - keine Bestellungen aus DB")

    return render_template("orders.html", orders=user_orders)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        app.logger.info("Settings form submitted")
        has_saved_data = False
        form_type = request.form.get("form_type")

        if form_type == "versandadresse_toggle":
            versandadresse_same = request.form.get("versandadresse_same") == "1"
            session["versandadresse_same"] = versandadresse_same

            if versandadresse_same and session.get("adresse"):
                session["versandadresse"] = dict(session.get("adresse", {}))
            elif not versandadresse_same:
                aktuelle_versandadresse = session.get("versandadresse", {})
                if aktuelle_versandadresse == session.get("adresse", {}):
                    session.pop("versandadresse", None)

            return redirect(url_for("settings") + "#konto-profil")

        def is_valid_plz(value):
            return bool(re.fullmatch(r"\d{4}", value.strip()))

        def is_valid_text(value):
            return bool(re.fullmatch(r"[A-Za-zÄÖÜäöüß\s\-]+", value.strip()))
        
        # Adresse Daten
        strasse = (request.form.get("strasse") or "").strip()
        plz = (request.form.get("plz") or "").strip()
        stadt = (request.form.get("stadt") or "").strip()
        land = (request.form.get("land") or "").strip()
        
        # Versandadresse Daten
        versand_strasse = (request.form.get("versand_strasse") or "").strip()
        versand_plz = (request.form.get("versand_plz") or "").strip()
        versand_stadt = (request.form.get("versand_stadt") or "").strip()
        versand_land = (request.form.get("versand_land") or "").strip()
        
        # Speichere in Session (oder DB wenn gewünscht)
        if strasse or plz or stadt or land:
            if strasse and plz and stadt and land and is_valid_plz(plz) and is_valid_text(stadt) and is_valid_text(land):
                session['adresse'] = {
                    'strasse': strasse,
                    'plz': plz,
                    'stadt': stadt,
                    'land': land
                }
                if session.get("versandadresse_same"):
                    session["versandadresse"] = dict(session["adresse"])

                # Speichere auch in Datenbank wenn User eingeloggt ist
                login_id = session.get('login_id')
                if login_id:
                    save_user_address(login_id, strasse, plz, stadt, land, is_shipping=False)
                    if session.get("versandadresse_same"):
                        save_user_address(login_id, strasse, plz, stadt, land, is_shipping=True)

                has_saved_data = True
                print("=== Adresse gespeichert ===")
                print(f"Straße: {strasse}")
                print(f"PLZ: {plz}")
                print(f"Stadt: {stadt}")
                print(f"Land: {land}")
                print("===========================")
            else:
                return redirect(url_for("settings", saved="0", error="format") + "#konto-profil")
        
        if versand_strasse or versand_plz or versand_stadt or versand_land:
            if versand_strasse and versand_plz and versand_stadt and versand_land and is_valid_plz(versand_plz) and is_valid_text(versand_stadt) and is_valid_text(versand_land):
                session['versandadresse'] = {
                    'strasse': versand_strasse,
                    'plz': versand_plz,
                    'stadt': versand_stadt,
                    'land': versand_land
                }

                # Speichere auch in Datenbank wenn User eingeloggt ist
                login_id = session.get('login_id')
                if login_id:
                    save_user_address(login_id, versand_strasse, versand_plz, versand_stadt, versand_land, is_shipping=True)

                has_saved_data = True
                print("=== Versandadresse gespeichert ===")
                print(f"Straße: {versand_strasse}")
                print(f"PLZ: {versand_plz}")
                print(f"Stadt: {versand_stadt}")
                print(f"Land: {versand_land}")
                print("===================================")
            else:
                return redirect(url_for("settings", saved="0", error="format") + "#konto-profil")
        
        # Redirect zurück zu settings mit konto-profil anchor
        if has_saved_data:
            if form_type in ("adresse", "versandadresse"):
                return redirect(url_for("profil"))
            return redirect(url_for("settings", saved="1") + "#konto-profil")
        return redirect(url_for("settings", saved="0") + "#konto-profil")
    
    return render_template(
        "settings.html",
        adresse=session.get("adresse", {}),
        versandadresse=session.get("versandadresse", {}),
        versandadresse_same=session.get("versandadresse_same", False),
    )

@app.route("/logout")
def logout():
    # Prüfe ob User überhaupt eingeloggt ist
    if not session.get('user_id'):
        # Nicht eingeloggt - zur Home-Seite weiterleiten
        return redirect(url_for("home"))

    # Session löschen beim Ausloggen
    session.clear()
    return render_template("logout.html")

@app.route("/do_logout")
def do_logout():
    # Alle Session-Daten löschen (wie Browser schließen)
    session.clear()
    return redirect(url_for("home"))


@app.route("/warenkorb")
def warenkorb():
    return render_template("warenkorb.html")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        app.logger.info("Checkout submitted")

        # Address Details
        salutation = request.form.get("salutation")
        name = request.form.get("name")
        surname = request.form.get("surname")
        address = request.form.get("address")
        plz = request.form.get("plz")
        city = request.form.get("city")
        tel = request.form.get("tel")
        email = request.form.get("email")

        # Card Details
        payment = request.form.get("payment")
        card_name = request.form.get("card_name")
        card_number = request.form.get("card_number")
        expiration = request.form.get("expiration")
        cvv = request.form.get("cvv")

        # ... (Print-Statements bleiben) ...

        # Adresse und Zahlung in DB speichern und IDs zurückbekommen
        customer_addres_id = add_customer_addres(salutation,name,surname,address,plz,city,tel,email)
        customer_payment_id = add_customer_payment(payment,card_name,card_number,expiration,cvv)

        # Warenkorb-Items aus dem Formular holen (vom Frontend gesendet)
        cart_data_str = request.form.get('cart_data', '[]')
        try:
            cart_items = json.loads(cart_data_str)
            print(f"📦 Warenkorb vom Frontend empfangen: {len(cart_items)} Items")
            for item in cart_items:
                print(f"   - {item.get('name', 'Unbekannt')}: {item.get('quantity', 1)}x CHF {item.get('price', 0)}")
        except json.JSONDecodeError:
            cart_items = []
            print("⚠️ Konnte Warenkorb-Daten nicht parsen")

        # Falls keine Cart-Items, erstelle Standard-Item
        if not cart_items:
            cart_items = [{'name': 'Floravis Seife', 'quantity': 1, 'price': 11.99}]

        # Total berechnen
        order_total = sum(item.get('quantity', 1) * item.get('price', 11.99) for item in cart_items)

        # Login-ID holen (falls User eingeloggt ist)
        login_id = session.get('login_id')

        # ========================================
        # BESTELLUNG IN DATENBANK SPEICHERN
        # ========================================
        order_id = create_order(
            login_id=login_id,
            customer_addres_id=customer_addres_id,
            customer_payment_id=customer_payment_id,
            total=order_total,
            items=cart_items
        )

        if order_id:
            print(f"✅ Bestellung {order_id} in Datenbank gespeichert!")
        else:
            print("⚠️ Bestellung konnte nicht in DB gespeichert werden")

        # ═══════════════════════════════════════════════════════════════
        # HIER FEHLT DEINE E-MAIL-LOGIK! 👇
        # ═══════════════════════════════════════════════════════════════
        # Order-Daten für E-Mail zusammenstellen
        order_data = {
            'salutation': salutation,
            'name': name,
            'surname': surname,
            'address': address,
            'plz': plz,
            'city': city,
            'tel': tel,
            'payment': payment,
            'items': cart_items,
            'total': order_total
        }

        # Bestätigungs-E-Mail senden
        recipient_name = f"{surname} {name}"
        if email:
            try:
                send_order_confirmation(email, recipient_name, order_data)
                print(f"📧 Bestätigungs-E-Mail an {email} gesendet!")
            except Exception as e:
                print(f"⚠️ E-Mail konnte nicht gesendet werden: {e}")
        # ═══════════════════════════════════════════════════════════════

        # Session-Daten löschen nach erfolgreichem Checkout
        session.pop('checkout_data', None)
        session.pop('cart', None)  # Warenkorb leeren

        return "OK", 200

    # GET: Lade gespeicherte Daten aus Session
    checkout_data = session.get('checkout_data', {})
    return render_template("checkout.html", checkout_data=checkout_data)
# Route zum Speichern der Checkout-Daten in der Session
@app.route("/save_checkout_data", methods=["POST"])
def save_checkout_data():
    data = request.get_json()
    if data:
        session['checkout_data'] = data
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route("/shop")
def shop() -> str:
    category = request.args.get("category", "").strip()
    if category:
        products = db_repo.get_products_by_category(category)
    else:
        products = db_repo.get_all_products_local()
    return render_template("shop.html", products=products, category=category)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = db_repo.get_product_by_id(product_id)
    if product is None:
        return redirect(url_for("shop"))
    # Get related products (same category, excluding current)
    related = [p for p in db_repo.get_products_by_category(product["category"]) if p["id"] != product_id][:3]
    return render_template("product_detail.html", product=product, related=related)  

@app.route("/search")
def search() -> str:
    query = request.args.get("q", "").strip()
    product_results = []

    if query:
        product_results = db_repo.search_products(query)

    pages = [
        {
            "title": "Home",
            "url": url_for("home"),
            "hint": "Homepage and Highlights",
            "keywords": ["home", "start", "floravis"],
        },
        {
            "title": "Shop",
            "url": url_for("shop"),
            "hint": "Soaps and Sets",
            "keywords": ["products", "soaps", "sets"],
        },
        {
            "title": "About us",
            "url": url_for("about_us"),
            "hint": "Our Story",
            "keywords": ["about", "brand", "story"],
        },
        {
            "title": "Contact",
            "url": url_for("contact"),
            "hint": "Contact Us",
            "keywords": ["kontakt", "help", "support"],
        },
        {
            "title": "Profile",
            "url": url_for("profil"),
            "hint": "Login and Profile",
            "keywords": ["login", "profile", "account"],
        },
        {
            "title": "Settings",
            "url": url_for("settings"),
            "hint": "Settings",
            "keywords": ["settings", "preferences"],
        },
    ]

    page_results = []
    if query:
        q_lower = query.lower()
        for page in pages:
            haystack = " ".join([page["title"], page["hint"]] + page["keywords"]).lower()
            if q_lower in haystack:
                page_results.append(page)

    return render_template(
        "search_results.html",
        query=query,
        products=product_results,
        pages=page_results,
    )

@app.route("/searchbar")
def searchbar() -> str:
    return render_template("searchbar.html")

@app.route("/add-product", methods=["POST"])
def add_product():
    name = request.form["name"]
    price = request.form["price"]
    db_repo.add_product(name, price)
    return redirect(url_for("home"))

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/shipping")
def shipping():
    return render_template("shipping.html")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
