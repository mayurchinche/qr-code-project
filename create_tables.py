from db import get_db_connection


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS product_documents (
        model_name VARCHAR(255) NOT NULL,
        serial_number VARCHAR(255) PRIMARY KEY,
        invoice_url VARCHAR(500) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    connection.close()
    print("✅ Table 'product_documents' created successfully!")


if __name__ == "__main__":
    create_tables()
