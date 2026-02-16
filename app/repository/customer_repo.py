from tarfile import data_filter

from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash


def add_customer_addres(salutation,name,surname,address,postal_code,city,tel,email):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT salutation_id FROM salutation WHERE salutation = %s", (salutation,))
        row = cur.fetchone()
        salutation_id = row[0] if row else None
        print(salutation_id)
        cur.execute("INSERT INTO customer_addres (salutation_id,name,surname,address,postal_code,city,tel,email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (salutation_id,name,surname,address,postal_code,city,tel,email))
        conn.commit()

    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        cur.close()

def add_customer_payment(payment_method,card_name,card_number,expiry_date,cvv):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO customer_payment (payment_method,card_name,card_number,expiry_date,cvv) VALUES (%s, %s, %s, %s, %s)",
                    (payment_method,card_name,card_number,expiry_date,cvv))
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
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


def get_all_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return products