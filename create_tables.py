from db import get_db_connection


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS product_details (
        model_name VARCHAR(255) NOT NULL,
        serial_number VARCHAR(255) NOT NULL,
        material_url VARCHAR(500) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (model_name, serial_number)  -- Composite Primary Key
    );
    """
    cursor.execute(create_table_query)
    connection.commit()

    print("✅ Table 'product_details' created successfully!")

    create_table_query = """
        CREATE TABLE IF NOT EXISTS product_queries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL,
            serial_number VARCHAR(255) NOT NULL,
            customer_gmail VARCHAR(255) NOT NULL,
            customer_city VARCHAR(255) NOT NULL,
            company_name VARCHAR(255) NOT NULL,
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
