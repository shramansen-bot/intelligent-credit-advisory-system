from engine.database import get_database_connection


def enable_pgvector():
    """
    Enable the pgvector PostgreSQL extension.

    The pgvector extension must already be installed on the
    PostgreSQL server before this command can succeed.
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE EXTENSION IF NOT EXISTS vector;"
            )

        connection.commit()


def create_tables():
    """
    Create all PostgreSQL tables required by the
    Intelligent Credit Advisory System.
    """

    statements = [
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL,
            monthly_net_income NUMERIC(12, 2) NOT NULL,
            existing_monthly_obligations NUMERIC(12, 2) NOT NULL,
            monthly_expenses NUMERIC(12, 2),
            credit_score INTEGER NOT NULL,
            employment_type VARCHAR(50) NOT NULL,
            kyc_status VARCHAR(50) NOT NULL,
            income_proof_verified BOOLEAN NOT NULL,
            employment_years NUMERIC(6, 2),
            fraud_review_flag BOOLEAN NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS loan_products (
            product_id VARCHAR(50) PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            description TEXT,
            annual_interest_rate NUMERIC(6, 3) NOT NULL,
            min_loan_amount NUMERIC(12, 2) NOT NULL,
            max_loan_amount NUMERIC(12, 2) NOT NULL,
            min_tenure_months INTEGER NOT NULL,
            max_tenure_months INTEGER NOT NULL,
            min_credit_score INTEGER NOT NULL,
            max_foir_percent NUMERIC(6, 2) NOT NULL,
            min_age INTEGER,
            max_age INTEGER,
            allowed_employment_types TEXT[]
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS loan_applications (
            application_id BIGSERIAL PRIMARY KEY,
            customer_id VARCHAR(20) NOT NULL
                REFERENCES customers(customer_id),
            product_id VARCHAR(50) NOT NULL
                REFERENCES loan_products(product_id),
            requested_amount NUMERIC(12, 2) NOT NULL,
            requested_tenure INTEGER NOT NULL,
            estimated_emi NUMERIC(12, 2),
            foir NUMERIC(6, 2),
            risk_level VARCHAR(20),
            risk_points INTEGER,
            decision VARCHAR(30),
            status VARCHAR(30) NOT NULL
                DEFAULT 'SUBMITTED',
            created_at TIMESTAMPTZ NOT NULL
                DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            audit_id BIGSERIAL PRIMARY KEY,
            application_id BIGINT
                REFERENCES loan_applications(application_id)
                ON DELETE CASCADE,
            agent_name VARCHAR(100) NOT NULL,
            action TEXT NOT NULL,
            details JSONB,
            created_at TIMESTAMPTZ NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS policy_chunks (
            chunk_id BIGSERIAL PRIMARY KEY,
            source_name VARCHAR(255) NOT NULL,
            source_type VARCHAR(50),
            source_title TEXT,
            source_url TEXT,
            chunk_text TEXT NOT NULL,
            embedding VECTOR(768) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)

        connection.commit()


def initialize_database():
    """
    Initialize the complete PostgreSQL database schema.
    """

    print(
        "Initializing PostgreSQL database..."
    )

    print(
        "Enabling pgvector extension..."
    )

    enable_pgvector()

    print(
        "Creating database tables..."
    )

    create_tables()

    print()
    print(
        "Database initialization completed successfully."
    )

    print()
    print(
        "Created/verified PostgreSQL extension:"
    )

    print(
        "- vector (pgvector)"
    )

    print()
    print(
        "Created/verified tables:"
    )

    print(
        "- customers"
    )

    print(
        "- loan_products"
    )

    print(
        "- loan_applications"
    )

    print(
        "- audit_logs"
    )

    print(
        "- policy_chunks"
    )


if __name__ == "__main__":
    initialize_database()