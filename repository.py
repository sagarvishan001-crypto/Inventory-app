from db import get_connection

def add_product(name, price, stock):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) RETURNING id",
                (name, price, stock),
            )
            return cur.fetchone()[0]

def list_products():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute (
                "SELECT id, name, price, stock FROM products ORDER BY id"
            )    
            return cur.fetchall()

def update_stock(product_id, new_stock):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute (
                "UPDATE products SET stock = %s WHERE id =%s",
                (new_stock, product_id),
            )
            return cur.rowcount

def low_stock(threshold):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute (
                "SELECT id, name, price, stock FROM products WHERE stock < %s ORDER BY stock",
                (threshold,),
            )           
            return cur.fetchall()

def delete_product(produc_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM products WHERE id = %s",
                (produc_id,),
            )
            return cur.rowcount