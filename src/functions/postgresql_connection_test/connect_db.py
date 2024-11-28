import os
import psycopg2
import requests
from azure.identity import DefaultAzureCredential


def connect_to_db():
    """Connects to the PostgreSQL database using environment variables."""
    # Fetch environment variables
    print("Fetching variables.")
    db_host = os.getenv("HOST")
    db_port = os.getenv("PORT")
    db_port = 5432
    db_name = os.getenv("DBNAME")
    db_user = os.getenv("USER")

    credential = DefaultAzureCredential()
    token = credential.get_token("https://ossrdbms-aad.database.windows.net")
    access_token = token.token
    print(f"access_token: {access_token}!")

    print("Fetching variables.")
    print(f"db_host: {db_host}!")
    print(f"db_name: {db_name}!")
    print(f"db_user: {db_user}!")

    if not all([db_host, db_port, db_name, db_user]):
        print("Error: Missing one or more required environment variables (host, port, dbname, user).")
        return

    # Fetch access token for authentication
    token = access_token
    print(f"token: {token}!")
    if not token:
        print("Failed to retrieve access token. Exiting.")
        return

    # Connection string
    connection_string = {
        "host": db_host,
        "port": db_port,
        "dbname": db_name,
        "user": db_user,
        "password": token,
        "sslmode": "require"
    }

    try:
        # Connect to the database
        conn = psycopg2.connect(**connection_string)
        print(f"Successfully connected to the database: {db_name}!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    connect_to_db()
