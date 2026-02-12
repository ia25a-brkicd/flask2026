-- Drop existing tables to recreate with correct structure
DROP TABLE IF EXISTS customer_payment CASCADE;
DROP TABLE IF EXISTS customer_payment_data CASCADE;
DROP TABLE IF EXISTS customer_addres CASCADE;

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

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




