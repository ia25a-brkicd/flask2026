import db
import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv # Lädt .env Datei
from mail import send_simple_message, send_order_confirmation
from repository.customer_repo import add_customer_addres, add_customer_payment, add_login, get_login_by_email, verify_login
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

        existing_login = get_login_by_email(email)
        if existing_login:
            return jsonify({"error": "Du hast bereits ein Konto mit dieser E-Mail."}), 409

        add_login(email, firstname, lastname, password)

        # HIER: "einloggen"
        session['user_id'] = email
        session['user_name'] = firstname
        session['user_lastname'] = lastname

        return jsonify({"success": True}), 200

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

    error_message = None
    if request.args.get("error") == "no_account":
        error_message = "Du hast noch kein Konto. Bitte registriere dich zuerst."

    return render_template("profil.html", user_profile=user_profile, error_message=error_message)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        app.logger.info("Login submitted")
        email = request.form.get("email")
        password = request.form.get("password")

        print("=== Login Form Data ===")
        print(f"E-Mail: {email}")
        print(f"Passwort: {password}")
        print("=======================")

        is_valid_login, row = verify_login(email, password)
        if not row:
            return redirect(url_for("profil", error="no_account"))

        if not is_valid_login:
            return render_template("login.html", error_message="E-Mail oder Passwort ist falsch.")

        session['user_id'] = row[1]
        session['user_name'] = row[2]
        session['user_lastname'] = row[3]

        return redirect(url_for("profil"))

    return render_template("login.html")


@app.route("/orders")
def orders():
    return render_template("orders.html")

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
    # Session-Daten bleiben erhalten beim Reload
    # Sie werden nur gelöscht, wenn der Browser geschlossen wird
    user_data = {
        'lastname': session.get('user_lastname', '-'),
        'firstname': session.get('user_name', '-'),
        'email': session.get('user_id', '-'),
        'password': '********' if session.get('user_id') else '-'
    }
    return render_template("logout.html", user=user_data)

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

        print("=== Checkout Form Data ===")
        print(f"Anrede: {salutation}")
        print(f"Name: {name}")
        print(f"Vorname: {surname}")
        print(f"Adresse: {address}")
        print(f"PLZ: {plz}")
        print(f"Ort: {city}")
        print(f"Telefon: {tel}")
        print(f"E-Mail: {email}")
        print(f"Zahlungsart: {payment}")
        print(f"Kartenname: {card_name}")
        print(f"Kartennummer: {card_number}")
        print(f"Ablaufdatum: {expiration}")
        print(f"CVV: {cvv}")
        print("==========================")

        add_customer_addres(salutation,name,surname,address,plz,city,tel,email)
        add_customer_payment(payment,card_name,card_number,expiration,cvv)



        # Session-Daten löschen nach erfolgreichem Checkout
        session.pop('checkout_data', None)

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
