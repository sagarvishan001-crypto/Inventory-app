# from db import get_connection

# with get_connection() as conn:

    # with conn.cursor() as cur:
    #     cur.execute("""
    #         CREATE TABLE IF NOT EXISTS products (
    #         id SERIAL PRIMARY KEY,
    #         name TEXT NOT NULL UNIQUE,
    #         price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    #         stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
    #         )
    #     """ )

    #     products = [
    #         ("Keyboard", 49.99, 10),
    #         ("Mouse", 19.99, 25),
    #         ("Monitor", 189.50, 7),
    #         ("USB Cable", 4.99, 100),
    #         ("Laptop Stand", 29.00, 15),
    #     ]

    #     cur.executemany(
    #         "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) "
    #         "ON CONFLICT (name) DO NOTHING",
    #         products,
    #     )

    #     cur.execute("SELECT id, name, price, stock FROM products")
    #     for row in cur.fetchall():
    #         print(row)

import psycopg
from db import get_connection

def add_product(name, price, stock):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) "
                "RETURNING id",
                (name, price, stock),
            )
            return cur.fetchone()[0]

for test in [("Keyboard", 10, 5), ("Cable2", -5, 5), ("Cable3", 5, -1)]:
    try:
        add_product(*test)
    except psycopg.errors.UniqueViolation:
        print(test[0], "-> duplicate name rejected")
    except psycopg.errors.CheckViolation:
        print(test[0], "-> negative value rejected")