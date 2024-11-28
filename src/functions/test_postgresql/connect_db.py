import os
import psycopg2

def get_access_token():
    """Fetches the access token using the Azure CLI."""
    try:
        import subprocess
        token = subprocess.check_output(
            ["az", "account", "get-access-token", "--resource-type", "oss-rdbms", "-o", "tsv", "--query", "accessToken"],
            text=True
        ).strip()
        return token
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

def connect_to_db():
    """Connects to the PostgreSQL database using environment variables."""
    # Fetch environment variables
    db_host = os.getenv("host")
    db_port = os.getenv("port")
    db_name = os.getenv("dbname")
    db_user = os.getenv("user")

    if not all([db_host, db_port, db_name, db_user]):
        print("Error: Missing one or more required environment variables (host, port, dbname, user).")
        return

    # Fetch access token for authentication
    token = get_access_token()
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
