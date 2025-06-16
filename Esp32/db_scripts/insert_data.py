import json
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_DB = os.getenv("MYSQL_DB")

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_table_if_not_exists(connection):
    cursor = connection.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS measurements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        minutes TIME NOT NULL,
        humidity FLOAT NOT NULL,
        temperature_c FLOAT NOT NULL,
        UNIQUE(date, minutes)  
    );
    '''
    cursor.execute(create_table_query)
    connection.commit()

def get_total_records(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM measurements;")
    total_records = cursor.fetchone()[0]
    return total_records

def insert_data_into_db(connection, data_list):
    cursor = connection.cursor()
    new_entries = 0

    check_query = "SELECT COUNT(*) FROM measurements WHERE date = %s AND minutes = %s;"
    insert_query = '''
    INSERT INTO measurements (date, minutes, humidity, temperature_c)
    VALUES (%s, %s, %s, %s);
    '''

    for data in data_list:
        cursor.execute(check_query, (data['date'], data['minutes']))
        if cursor.fetchone()[0] == 0:
            cursor.execute(insert_query, (data['date'], data['minutes'], data['humidity'], data['temperature_c']))
            new_entries += 1

    connection.commit()
    return new_entries

def insert_data_into_mongodb(data_list):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["esp32"]
        collection = db["measurements"]

        new_entries = 0

        for data in data_list:
            query = {"date": data["date"], "minutes": data["minutes"]}
            if collection.count_documents(query) == 0:
                collection.insert_one(data)
                new_entries += 1

        print(f"(MongoDB) New entries inserted: {new_entries}")
        client.close()
    except ConnectionFailure as e:
        print(f"Error connecting to MongoDB: {e}")

def main():
    json_file = 'Cleaned_data.json'
    try:
        with open(json_file, 'r') as file:
            data_list = json.load(file)
            if not isinstance(data_list, list):
                data_list = [data_list]
    except FileNotFoundError:
        print("JSON file not found!")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    connection = connect_to_database()
    if connection:
        create_table_if_not_exists(connection)
        before_count = get_total_records(connection)
        new_entries = insert_data_into_db(connection, data_list)
        after_count = get_total_records(connection)

        print(f"(Mysql) New entries inserted: {new_entries}")
        connection.close()

    insert_data_into_mongodb(data_list)

if __name__ == "__main__":
    main()
