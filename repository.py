from db import get_connection

class InsufficientStock(Exception):
    pass

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
        
def place_order(user_id, items):
    """Items is a list of (product_id, quantity) tuples."""
    # Merge duplicates and sort by product_id so current orders
    # Locks row in same order (prevents deadlock)
    merged = {}
    for product_id, qty in items:
        merged[product_id] = merged.get(product_id, 0) + qty

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (user_id) values (%s) RETURNING id",
                (user_id,),
            ) 
            order_id = cur.fetchone()[0]

            for product_id in sorted(merged):
                qty = merged[product_id]

                # FOR UPDATE locks this row until the transaction ends
                cur.execute(
                    "SELECT price, stock FROM products WHERE id = %s FOR UPDATE",
                    (product_id,),
                )
                row=cur.fetchone()
                if row is None:
                    raise ValueError(f"Product {product_id} does not exists")

                price, stock = row

                if stock < qty:
                    raise InsufficientStock(
                        f"Product {product_id}: Only {stock} left, wanted {qty} "
                    )

                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (qty, product_id),
                )
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
                    "VALUES (%s, %s, %s,%s)",
                    (order_id, product_id, qty, price),
                )
            return order_id