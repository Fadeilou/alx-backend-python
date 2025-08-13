from dotenv import load_dotenv
import mysql.connector
import csv
import uuid
import os


load_dotenv()

def connect_db():
    """
    Connect to the MySQL database server.
    """
    user = os.getenv('SQL_USERNAME')
    password = os.getenv('SQL_PASSWORD')
    host = 'localhost'
    try:
        mysql_connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host
        )
        return mysql_connection
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_database(connection):
    """
    Create a new database.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

def connect_to_prodev():
    """
    Connect to the prodev database.
    """
    user = os.getenv('SQL_USERNAME')
    password = os.getenv('SQL_PASSWORD')
    host = 'localhost'
    try:
        mysql_connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database="ALX_prodev"
        )
        return mysql_connection
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_table(connection):
    """
    Create a new table.
    """
    try:
        cursor = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX (user_id)
                );
                """
        cursor.execute(query)
        connection.commit()
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

def insert_data(connection, data):
    """
    Insert data into the table.
    """
    try:
        cursor = connection.cursor()
        with open (data, 'r') as file:
            csv_data = csv.DictReader(file)
            for row in csv_data:
                user_id = str(uuid.uuid4())
                name = row["name"]
                email = row["email"]
                age = row["age"]
                query = "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (user_id, name, email, age))
            connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
            