#!/usr/bin/python3
"""
Script to set up and seed the MySQL database ALX_prodev with user_data.
"""
import mysql.connector
import csv
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "ALX_prodev"


def connect_db():
    """Connects to the MySQL database server."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None


def create_database(connection):
    """Creates the database ALX_prodev if it does not exist."""
    if not connection:
        return
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database {DB_NAME} ensured.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")


def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database {DB_NAME}: {err}")
        return None


def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields."""
    if not connection:
        return
    try:
        cursor = connection.cursor()
        table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age INT NOT NULL,
            INDEX(user_id)
        );
        """
        # Note: VARCHAR for user_id as UUIDs are strings. INT for age.
        # MySQL automatically indexes PRIMARY KEY. Explicit INDEX(user_id) is redundant but harmless.
        cursor.execute(table_query)
        print("Table user_data created successfully or already exists.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table user_data: {err}")


def insert_data(connection, csv_filepath):
    """Inserts data in the database from a CSV file if it does not exist."""
    if not connection:
        return
    
    cursor = connection.cursor()
    
    # Check if table is empty. If not, assume data might exist.
    # For a robust "if it does not exist" per row, we'd need INSERT IGNORE or ON DUPLICATE KEY UPDATE.
    # Or, count existing rows to decide.
    # Given the prompt "inserts data ... if it does not exist", it might imply skip if any data exists,
    # or be more granular. Let's use INSERT IGNORE for row-level idempotency.
    
    try:
        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            data_to_insert = []
            for row in csv_reader:
                # Ensure age is an integer
                try:
                    age = int(float(row['age'])) # CSV might have age as float like "67.0"
                except ValueError:
                    print(f"Skipping row due to invalid age: {row}")
                    continue
                data_to_insert.append((
                    row['user_id'],
                    row['name'],
                    row['email'],
                    age
                ))

            if data_to_insert:
                # Using INSERT IGNORE to skip inserting rows with duplicate primary keys (user_id)
                insert_query = """
                INSERT IGNORE INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                cursor.executemany(insert_query, data_to_insert)
                connection.commit()
                print(f"Inserted {cursor.rowcount} new rows into user_data. {len(data_to_insert) - cursor.rowcount} rows were duplicates or ignored.")
            else:
                print("No data to insert from CSV.")
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_filepath}' not found.")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
    except Exception as e:
        print(f"An unexpected error occurred during data insertion: {e}")
    finally:
        if cursor:
            cursor.close()


if __name__ == '__main__':
    # This part is for testing the seed script directly
    # The 0-main.py will call these functions as well.
    print("Running seed script...")
    conn = connect_db()
    if conn:
        create_database(conn)
        conn.close() # Close initial connection, connect_to_prodev will make a new one
        print("Database creation step successful.")

        prodev_conn = connect_to_prodev()
        if prodev_conn:
            create_table(prodev_conn)
            # Ensure user_data.csv is in the same directory or provide full path
            insert_data(prodev_conn, 'user_data.csv')
            
            # Verification steps (similar to 0-main.py)
            cursor = prodev_conn.cursor()
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{DB_NAME}';")
            result = cursor.fetchone()
            if result:
                print(f"Database {DB_NAME} is present.")
            
            cursor.execute(f"SELECT COUNT(*) FROM user_data;")
            count_result = cursor.fetchone()
            print(f"Total rows in user_data: {count_result[0] if count_result else 'N/A'}")

            cursor.execute(f"SELECT * FROM user_data LIMIT 2;")
            rows = cursor.fetchall()
            print("Sample data from user_data:")
            for row in rows:
                print(row)
            
            cursor.close()
            prodev_conn.close()
            print("Seeding process complete.")
        else:
            print("Failed to connect to ALX_prodev for table creation and data insertion.")
    else:
        print("Failed to connect to MySQL server.")
