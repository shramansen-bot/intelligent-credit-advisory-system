import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_database_connection():
    """
    Create and return a PostgreSQL database connection.

    Database credentials are loaded from environment variables
    so that secrets are never hardcoded in the source code.
    """
    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise ValueError(
            "Missing required database environment variables: "
            + ", ".join(missing_variables)
        )

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def test_database_connection():
    """
    Verify that Python can connect to PostgreSQL.
    """
    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user, version();"
            )
            return cursor.fetchone()


if __name__ == "__main__":
    database_name, database_user, database_version = (
        test_database_connection()
    )

    print("PostgreSQL connection successful.")
    print(f"Database: {database_name}")
    print(f"User: {database_user}")
    print(f"Version: {database_version}")