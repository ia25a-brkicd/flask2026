-- Drop existing tables to recreate with correct structure
DROP TABLE IF EXISTS customer_payment CASCADE;
DROP TABLE IF EXISTS customer_payment_data CASCADE;
DROP TABLE IF EXISTS customer_addres CASCADE;



CREATE TABLE IF NOT EXISTS salutation (
    salutation_id SERIAL PRIMARY KEY,
    salutation VARCHAR(20) NOT NULL
);

INSERT INTO salutation (salutation) VALUES ('Herr'), ('Frau'), ('Keine') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS customer_addres (
    customer_addres_id SERIAL primary key,
    salutation_id INT NOT NULL REFERENCES salutation(salutation_id),
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    address VARCHAR(100) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    city VARCHAR(50) NOT NULL,
    tel VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_payment (
    customer_payment_id SERIAL primary key,
    payment_method VARCHAR(50) NOT NULL,
    card_name VARCHAR(50) NOT NULL,
    card_number VARCHAR(20) NOT NULL,
    expiry_date VARCHAR(5) NOT NULL,
    cvv VARCHAR(4) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_addres_id INT NOT NULL REFERENCES customer_addres(customer_addres_id),
    customer_payment_id INT NOT NULL REFERENCES customer_payment(customer_payment_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products_shop (
    product_shop_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id),
    stock INT
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE IF NOT EXISTS customer (
    email VARCHAR(100) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(50),
    customer_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id)
);

