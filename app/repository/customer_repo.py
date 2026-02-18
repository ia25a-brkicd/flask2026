from tarfile import data_filter

from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


def add_customer_addres(salutation,name,surname,address,postal_code,city,tel,email):
    """Fügt eine Kundenadresse hinzu und gibt die ID zurück"""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT salutation_id FROM salutation WHERE salutation = %s", (salutation,))
        row = cur.fetchone()
        salutation_id = row[0] if row else None
        print(salutation_id)
        cur.execute("""INSERT INTO customer_addres (salutation_id,name,surname,address,postal_code,city,tel,email) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING customer_addres_id""",
                    (salutation_id,name,surname,address,postal_code,city,tel,email))
        customer_addres_id = cur.fetchone()[0]
        conn.commit()
        return customer_addres_id

    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()

def add_customer_payment(payment_method,card_name,card_number,expiry_date,cvv):
    """Fügt Zahlungsdaten hinzu und gibt die ID zurück"""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO customer_payment (payment_method,card_name,card_number,expiry_date,cvv) 
                       VALUES (%s, %s, %s, %s, %s) RETURNING customer_payment_id""",
                    (payment_method,card_name,card_number,expiry_date,cvv))
        customer_payment_id = cur.fetchone()[0]
        conn.commit()
        return customer_payment_id
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()

#push test

def add_login(email, first_name, last_name, password):
    conn = get_db()
    cur = conn.cursor()
    try:
        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO login (email,first_name,last_name,password) VALUES (%s, %s, %s, %s)",
                     (email, first_name, last_name, hashed_password))
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        cur.close()


def get_login_by_email(email):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT login_id, email, first_name, last_name, password FROM login WHERE email = %s",
            (email,),
        )
        return cur.fetchone()
    finally:
        cur.close()


def verify_login(email, password):
    row = get_login_by_email(email)
    if not row:
        return False, None
    hashed_password = row[4]
    return check_password_hash(hashed_password, password), row


def get_all_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return products


# ========================================
# ORDER FUNKTIONEN
# ========================================

def create_order(login_id, customer_addres_id, customer_payment_id, total, items):
    """
    Erstellt eine neue Bestellung in der Datenbank.

    Parameters:
    - login_id: ID des eingeloggten Users (kann None sein für Gast-Bestellungen)
    - customer_addres_id: ID der Kundenadresse
    - customer_payment_id: ID der Zahlungsdaten
    - total: Gesamtbetrag
    - items: Liste von Produkten [{name, quantity, price}, ...]

    Returns:
    - order_id oder None bei Fehler
    """
    conn = get_db()
    cur = conn.cursor()
    try:
        # Order erstellen
        cur.execute("""
            INSERT INTO orders (login_id, customer_addres_id, customer_payment_id, total, status)
            VALUES (%s, %s, %s, %s, 'Bestätigt')
            RETURNING order_id
        """, (login_id, customer_addres_id, customer_payment_id, total))

        order_id = cur.fetchone()[0]

        # Order Items hinzufügen
        for item in items:
            cur.execute("""
                INSERT INTO order_items (order_id, product_name, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item.get('name', 'Produkt'), item.get('quantity', 1), item.get('price', 11.99)))

        conn.commit()
        print(f"✅ Bestellung {order_id} erfolgreich erstellt!")
        return order_id

    except Exception as e:
        print(f"Database error beim Erstellen der Bestellung: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()


def get_orders_by_login_id(login_id):
    """
    Holt alle Bestellungen eines Users aus der Datenbank.

    Parameters:
    - login_id: ID des Users

    Returns:
    - Liste von Bestellungen mit Items
    """
    conn = get_db()
    cur = conn.cursor()
    try:
        # Alle Bestellungen des Users holen
        cur.execute("""
            SELECT order_id, total, status, order_date
            FROM orders
            WHERE login_id = %s
            ORDER BY order_date DESC
        """, (login_id,))

        orders_rows = cur.fetchall()
        orders = []

        for order_row in orders_rows:
            order_id, total, status, order_date = order_row

            # Items für diese Bestellung holen
            items = []  # Immer als leere Liste initialisieren
            try:
                cur.execute("""
                    SELECT product_name, quantity, price
                    FROM order_items
                    WHERE order_id = %s
                """, (order_id,))

                items_rows = cur.fetchall()
                for item_row in items_rows:
                    items.append({
                        'name': item_row[0],
                        'quantity': item_row[1],
                        'price': float(item_row[2])
                    })
            except Exception as item_error:
                print(f"Fehler beim Laden der Items für Order {order_id}: {item_error}")
                # items bleibt leere Liste

            # Datum formatieren
            date_str = None
            if order_date:
                try:
                    date_str = order_date.isoformat()
                except:
                    date_str = str(order_date)

            orders.append({
                'order_id': order_id,
                'total': float(total) if total else 0.0,
                'status': status or 'Unbekannt',
                'date': date_str,
                'items': items  # Immer eine Liste
            })

        return orders

    except Exception as e:
        print(f"Database error beim Laden der Bestellungen: {e}")
        return []
    finally:
        cur.close()


def get_orders_by_email(email):
    """
    Holt alle Bestellungen anhand der E-Mail-Adresse.
    Sucht zuerst die login_id und dann die Bestellungen.
    """
    login_data = get_login_by_email(email)
    if not login_data:
        return []

    login_id = login_data[0]
    return get_orders_by_login_id(login_id)

