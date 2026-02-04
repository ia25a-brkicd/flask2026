import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv # Lädt .env Datei
from services import math_service
from config import DevelopmentConfig, ProductionConfig

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
    return render_template("contact.html")




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
    return render_template("profil.html")

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

if __name__ == '__main__':
    app.run(port=5000)
