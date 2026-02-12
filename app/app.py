import db
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv # Lädt .env Datei

from repository.customer_repo import add_customer_addres, add_customer_payment
from services import math_service
from config import DevelopmentConfig, ProductionConfig
from flask_mail import Mail, Message
from repository import product_repo as db_repo

# Definieren einer Variable, die die aktuelle Datei zum Zentrum
# der Anwendung macht.
app = Flask(__name__)
app.secret_key = 'floravis-secret-key-2026'  # Für Session-Cookies

"""
Festlegen einer Route für die Homepage. Der String in den Klammern
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
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "false").lower() == "true",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "true").lower() == "true",
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME")),
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
    return render_template("home.html")

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
    if request.method == "POST":
        app.logger.info("Form submitted")
        lastname = request.form.get("lastname")
        firstname = request.form.get("firstname")
        email = request.form.get("email")
        message = request.form.get("message")
        
        print("=== Contact Form Data ===")
        print(f"Name: {lastname}")
        print(f"Vorname: {firstname}")
        print(f"E-Mail: {email}")
        print(f"Nachricht: {message}")
        print("========================")

        recipient = os.getenv("MAIL_RECIPIENT")
        if recipient and app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
            try:
                msg = Message(
                    subject="Kontaktformular",
                    recipients=[recipient],
                    reply_to=email,
                    body=(
                        "Neue Nachricht vom Kontaktformular\n\n"
                        f"Nachname: {lastname}\n"
                        f"Vorname: {firstname}\n"
                        f"E-Mail: {email}\n\n"
                        f"Nachricht:\n{message}\n"
                    ),
                )
                mail.send(msg)
                app.logger.info("Contact email sent")
            except Exception:
                app.logger.exception("Failed to send contact email")
        else:
            app.logger.warning("Mail is not configured; skipping send")
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

        return redirect(url_for("home"))    # zurück zur Startseite

    # GET-Anfrage: nur Formular anzeigen
    # GET-Anfrage: nur Formular anzeigen
    return render_template("profil.html")


@app.route("/logout")
def logout():
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
    return render_template("shop.html")  

@app.route("/searchbar")
def searchbar() -> str:
    return render_template("searchbar.html")

@app.route("/add-product", methods=["POST"])
def add_product():
    name = request.form["name"]
    price = request.form["price"]
    db_repo.add_product(name, price)
    return redirect(url_for("home"))



if __name__ == '__main__':
    app.run(port=5000)





