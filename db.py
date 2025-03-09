import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print("Loaded Env Vars:", DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)


def get_db_connection():
    """Establish a database connection."""
    connection = mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection


# Test connection
try:
    conn = get_db_connection()
    print("✅ Database connection successful!")
    conn.close()
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
