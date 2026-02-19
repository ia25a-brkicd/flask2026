import os
import requests

# ============================================================
# MAILGUN KONFIGURATION - BITTE AUSFÜLLEN:
# ============================================================
# 1. API_KEY: Dein Mailgun API Key
#    - Findest du unter: https://app.mailgun.com/app/account/security/api_keys
#    - Beispiel: "key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#
# 2. DOMAIN: Deine Mailgun Domain
#    - Sandbox Domain: "sandboxXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.mailgun.org"
#    - Oder deine verifizierte Domain: "mail.deinedomain.com"
#
# 3. SENDER_EMAIL: Absender E-Mail
#    - Bei Sandbox: "postmaster@sandboxXXXX.mailgun.org"
#    - Bei eigener Domain: "noreply@deinedomain.com"
#
# 4. RECIPIENT: Empfänger E-Mail für Kontaktformular
#    - z.B.: "floravis05@gmail.com"
#
# Diese Werte kannst du in der .env Datei setzen:
# API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# DOMAIN=sandboxaac2dec4f1b445bf9c922b43c85e6d22.mailgun.org
# SENDER_EMAIL=postmaster@sandboxaac2dec4f1b445bf9c922b43c85e6d22.mailgun.org
# RECIPIENT=floravis05@gmail.com
# ============================================================

MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
MAILGUN_SENDER_EMAIL = os.getenv('MAILGUN_SENDER_EMAIL')

if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_SENDER_EMAIL]):
    raise RuntimeError("Missing Mailgun env vars: MAILGUN_API_KEY / MAILGUN_DOMAIN / MAILGUN_SENDER_EMAIL")


def send_order_confirmation(recipient_email, recipient_name, order_data):
    """
    Sendet eine Bestellbestätigung per E-Mail via Mailgun.

    Parameter:
    - recipient_email: E-Mail-Adresse des Kunden
    - recipient_name: Name des Kunden (Vorname Nachname)
    - order_data: Dictionary mit Bestellinformationen
        {
            'salutation': 'Herr/Frau',
            'name': 'Nachname',
            'surname': 'Vorname',
            'address': 'Strasse und Hausnummer',
            'plz': 'PLZ',
            'city': 'Ort',
            'tel': 'Telefonnummer',
            'payment': 'Zahlungsart',
            'items': [{'name': 'Produktname', 'quantity': 1, 'price': 11.99}, ...],
            'total': 23.98
        }

    Returns:
    - Response-Objekt von Mailgun API
    """

    # E-Mail Betreff
    subject = "Floravis - Bestellbestätigung"

    # Bestellpositionen formatieren
    items_text = ""
    if 'items' in order_data and order_data['items']:
        for item in order_data['items']:
            items_text += f"  - {item.get('name', 'Produkt')}: {item.get('quantity', 1)}x CHF {item.get('price', 11.99):.2f}\n"
    else:
        items_text = "  - Ihre Bestellung (Details folgen)\n"

    # Total berechnen
    total = order_data.get('total', 0)

    # E-Mail Text erstellen
    email_text = f"""
Liebe/r {order_data.get('salutation', '')} {order_data.get('surname', '')} {order_data.get('name', '')},

Vielen Dank für Ihre Bestellung bei Floravis!

Ihre Bestellung wurde erfolgreich aufgenommen.

═══════════════════════════════════════════
BESTELLÜBERSICHT
═══════════════════════════════════════════

Bestellte Artikel:
{items_text}
───────────────────────────────────────────
TOTAL: CHF {total:.2f}
═══════════════════════════════════════════

LIEFERADRESSE:
{order_data.get('salutation', '')} {order_data.get('surname', '')} {order_data.get('name', '')}
{order_data.get('address', '')}
{order_data.get('plz', '')} {order_data.get('city', '')}

Telefon: {order_data.get('tel', '-')}
E-Mail: {recipient_email}

ZAHLUNGSART: {order_data.get('payment', '-')}

═══════════════════════════════════════════

Ihre Bestellung wird in Kürze bearbeitet und versendet.
Bei Fragen stehen wir Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen,
Ihr Floravis Team

───────────────────────────────────────────
Floravis - Natürliche Seifen
www.floravis.ch
───────────────────────────────────────────
"""

    # HTML Version für bessere Darstellung
    email_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2d5016 0%, #4a7c23 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .order-box {{ background: white; border: 2px solid #2d5016; border-radius: 10px; padding: 20px; margin: 20px 0; }}
        .order-item {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .total {{ font-size: 20px; font-weight: bold; color: #2d5016; text-align: right; padding-top: 15px; }}
        .address-box {{ background: #fff; padding: 15px; border-left: 4px solid #4a7c23; margin: 20px 0; }}
        .footer {{ background: #2d5016; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
        .footer a {{ color: #a8d080; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌿 Floravis</h1>
            <p>Bestellbestätigung</p>
        </div>
        <div class="content">
            <p>Liebe/r {order_data.get('salutation', '')} {order_data.get('surname', '')} {order_data.get('name', '')},</p>
            <p><strong>Vielen Dank für Ihre Bestellung!</strong></p>
            <p>Ihre Bestellung wurde erfolgreich aufgenommen und wird in Kürze bearbeitet.</p>
            
            <div class="order-box">
                <h3 style="margin-top: 0; color: #2d5016;">📦 Bestellübersicht</h3>
                {''.join([f'<div class="order-item">{item.get("name", "Produkt")} - {item.get("quantity", 1)}x <strong>CHF {item.get("price", 11.99):.2f}</strong></div>' for item in order_data.get('items', [])]) or '<div class="order-item">Ihre Bestellung</div>'}
                <div class="total">Total: CHF {total:.2f}</div>
            </div>
            
            <div class="address-box">
                <h4 style="margin-top: 0;">📍 Lieferadresse</h4>
                <p style="margin: 0;">
                    {order_data.get('salutation', '')} {order_data.get('surname', '')} {order_data.get('name', '')}<br>
                    {order_data.get('address', '')}<br>
                    {order_data.get('plz', '')} {order_data.get('city', '')}
                </p>
            </div>
            
            <p><strong>💳 Zahlungsart:</strong> {order_data.get('payment', '-')}</p>
            
            <p>Bei Fragen stehen wir Ihnen gerne zur Verfügung.</p>
            <p>Mit freundlichen Grüßen,<br><strong>Ihr Floravis Team</strong></p>
        </div>
        <div class="footer">
            <p>🌿 Floravis - Natürliche Seifen</p>
            <p><a href="https://floravis.onrender.com">floravis.onrender.com</a></p>
        </div>
    </div>
</body>
</html>
"""

    try:
        print(f"📧 Versuche E-Mail zu senden...")
        print(f"   Domain: {MAILGUN_DOMAIN}")
        print(f"   Von: {MAILGUN_SENDER_EMAIL}")
        print(f"   An: {recipient_email}")
        print(f"   API Key (erste 10 Zeichen): {MAILGUN_API_KEY[:10]}...")

        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Floravis Shop <{MAILGUN_SENDER_EMAIL}>",
                "to": f"{recipient_name} <{recipient_email}>",
                "subject": subject,
                "text": email_text,
                "html": email_html
            }
        )

        print(f"📧 Mailgun Response Status: {response.status_code}")
        print(f"📧 Mailgun Response: {response.text}")

        if response.status_code == 200:
            print(f"✅ Bestätigungs-E-Mail erfolgreich an {recipient_email} gesendet!")
        else:
            print(f"❌ Fehler beim Senden der E-Mail: {response.status_code} - {response.text}")

        return response

    except Exception as e:
        print(f"❌ Mailgun Fehler: {e}")
        return None


def send_contact_message(firstname, lastname, email, message):
    """
    Sendet eine Kontaktformular-Nachricht per E-Mail via Mailgun.

    Parameter:
    - firstname: Vorname des Absenders
    - lastname: Nachname des Absenders
    - email: E-Mail-Adresse des Absenders
    - message: Nachricht vom Absender

    Returns:
    - Response-Objekt von Mailgun API
    """
    
    recipient_email = os.getenv('RECIPIENT', 'floravis05@gmail.com')
    
    # E-Mail Betreff
    subject = f"Neue Kontaktanfrage von {firstname} {lastname}"

    # E-Mail Text erstellen
    email_text = f"""
Neue Kontaktanfrage von der FlorAvis Webseite:

═══════════════════════════════════════════
KONTAKTDATEN
═══════════════════════════════════════════
Name: {firstname} {lastname}
Email: {email}

═══════════════════════════════════════════
NACHRICHT
═══════════════════════════════════════════
{message}

───────────────────────────────────────────
Diese Nachricht wurde über das Kontaktformular gesendet.
Antworten Sie direkt an: {email}
───────────────────────────────────────────
"""

    # HTML Version
    email_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #2d5016 0%, #4a7c23 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .info-box {{ background: white; border-left: 4px solid #4a7c23; padding: 15px; margin: 20px 0; }}
        .message-box {{ background: white; border: 2px solid #2d5016; border-radius: 10px; padding: 20px; margin: 20px 0; }}
        .footer {{ background: #2d5016; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
        .label {{ font-weight: bold; color: #2d5016; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌿 Floravis</h1>
            <p>Neue Kontaktanfrage</p>
        </div>
        <div class="content">
            <p><strong>Eine neue Nachricht wurde über das Kontaktformular gesendet:</strong></p>
            
            <div class="info-box">
                <p style="margin: 5px 0;"><span class="label">👤 Name:</span> {firstname} {lastname}</p>
                <p style="margin: 5px 0;"><span class="label">📧 Email:</span> <a href="mailto:{email}">{email}</a></p>
            </div>
            
            <div class="message-box">
                <h3 style="margin-top: 0; color: #2d5016;">💬 Nachricht</h3>
                <p style="white-space: pre-wrap;">{message}</p>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                <em>💡 Tipp: Sie können direkt auf diese E-Mail antworten, um dem Kunden zu schreiben.</em>
            </p>
        </div>
        <div class="footer">
            <p>🌿 Floravis Kontaktformular</p>
        </div>
    </div>
</body>
</html>
"""

    try:
        print(f"📧 Versuche Kontakt-Email zu senden...")
        print(f"   Domain: {MAILGUN_DOMAIN}")
        print(f"   Von: {MAILGUN_SENDER_EMAIL}")
        print(f"   An: {recipient_email}")

        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Floravis Kontaktformular <{MAILGUN_SENDER_EMAIL}>",
                "to": recipient_email,
                "subject": subject,
                "text": email_text,
                "html": email_html,
                "h:Reply-To": email
            }
        )

        print(f"📧 Mailgun Response Status: {response.status_code}")
        print(f"📧 Mailgun Response: {response.text}")

        if response.status_code == 200:
            print(f"✅ Kontakt-E-Mail erfolgreich an {recipient_email} gesendet!")
        else:
            print(f"❌ Fehler beim Senden der E-Mail: {response.status_code} - {response.text}")

        return response

    except Exception as e:
        print(f"❌ Mailgun Fehler: {e}")
        return None


