from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

import psycopg
import repository

app = FastAPI(title="Inventory API")

class ProductIn(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)

class StockIn(BaseModel):
    new_stock: int = Field(ge=0)

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=0)

class OrderIn(BaseModel):
    user_id: int
    items: list[OrderItemIn] = Field(min_length=1)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/products")
def get_products():
    rows = repository.list_products()
    return [
        {"id": r[0], "name": r[1], "price": float(r[2]), "stock": r[3]}
        for r in rows
    ]


@app.post("/products", status_code=201)
def create_product(product: ProductIn):
    try:
        new_id = repository.add_product(product.name, product.price, product.stock)
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail = "Product already exists" )
    return {"id": new_id, **product.model_dump()}

@app.put("/products/{product_id}/stock")
def update_product(product_id : int, product: StockIn):
    try:
        updated = repository.update_stock(product_id, product.new_stock)
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=422, detail = "Stock cannot be negetive")
    if updated == 0:
        raise HTTPException(status_code=404, detail = "Product not found")
    return {"id": product_id, "Stock": product.new_stock}

@app.delete("/products/{product_id}")
def delete_product(product_id : int):
    try:
        deleted = repository.delete_product(product_id)
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=405, detail= "Enter valid product id")
    if deleted == 0:
        raise HTTPException(status_code= 406, detail = "Product not found")
    return {"id": product_id}

@app.post("/orders", status_code=201)
def create_order(order: OrderIn):
    items = [(i.product_id, i.quantity) for i in order.items]
    try:
        order_id = repository.place_order(order.user_id, items)
    except repository.InsufficientStock as e:
        raise HTTPException(status = 409, detail = str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=404, detail="User does not exist")
    return {"order_id": order_id}
