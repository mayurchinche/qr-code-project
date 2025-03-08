import mysql.connector
import os

# Database connection details
DB_HOST = "mysql-oms-db-mayur-96fb.e.aivencloud.com"
DB_PORT = 11523
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_nv26JjtPYWRcDqIXGc7"
DB_NAME = "defaultdb"


def get_db_connection():
    """Establish a database connection."""
    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection
