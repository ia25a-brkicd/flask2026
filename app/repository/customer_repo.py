from db import get_db

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


def get_all_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return products