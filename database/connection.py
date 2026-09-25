import mysql.connector


def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Anu6421@#rag",
        database="CampusHub"
    )

    return connection