import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():

    if os.getenv("APP_ENV") == "test":
        dbname = os.getenv("TEST_DB_NAME")
    else:
        dbname = os.getenv("DB_NAME")

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=dbname,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )