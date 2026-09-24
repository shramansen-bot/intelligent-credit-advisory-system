from engine.data_loader import (
    load_customers,
    load_loan_products,
)
from engine.database import get_database_connection


def seed_customers(cursor):
    """
    Load synthetic customer data from JSON and insert
    or update it in PostgreSQL.
    """
    customers = load_customers()

    for customer in customers:
        cursor.execute(
            """
            INSERT INTO customers (
                customer_id,
                name,
                age,
                monthly_net_income,
                existing_monthly_obligations,
                monthly_expenses,
                credit_score,
                employment_type,
                kyc_status,
                income_proof_verified,
                employment_years,
                fraud_review_flag
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (customer_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                age = EXCLUDED.age,
                monthly_net_income =
                    EXCLUDED.monthly_net_income,
                existing_monthly_obligations =
                    EXCLUDED.existing_monthly_obligations,
                monthly_expenses =
                    EXCLUDED.monthly_expenses,
                credit_score =
                    EXCLUDED.credit_score,
                employment_type =
                    EXCLUDED.employment_type,
                kyc_status =
                    EXCLUDED.kyc_status,
                income_proof_verified =
                    EXCLUDED.income_proof_verified,
                employment_years =
                    EXCLUDED.employment_years,
                fraud_review_flag =
                    EXCLUDED.fraud_review_flag;
            """,
            (
                customer["customer_id"],
                customer["name"],
                customer["age"],
                customer["monthly_net_income"],
                customer[
                    "existing_monthly_obligations"
                ],
                customer["monthly_expenses"],
                customer["credit_score"],
                customer["employment_type"],
                customer["kyc_status"],
                customer["income_proof_verified"],
                customer["employment_years"],
                customer["fraud_flag"],
            ),
        )

    return len(customers)


def seed_loan_products(cursor):
    """
    Load synthetic loan product data from JSON and insert
    or update it in PostgreSQL.
    """
    products = load_loan_products()

    for product in products:
        cursor.execute(
            """
            INSERT INTO loan_products (
                product_id,
                product_name,
                description,
                annual_interest_rate,
                min_loan_amount,
                max_loan_amount,
                min_tenure_months,
                max_tenure_months,
                min_credit_score,
                max_foir_percent,
                min_age,
                max_age,
                allowed_employment_types
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (product_id)
            DO UPDATE SET
                product_name =
                    EXCLUDED.product_name,
                description =
                    EXCLUDED.description,
                annual_interest_rate =
                    EXCLUDED.annual_interest_rate,
                min_loan_amount =
                    EXCLUDED.min_loan_amount,
                max_loan_amount =
                    EXCLUDED.max_loan_amount,
                min_tenure_months =
                    EXCLUDED.min_tenure_months,
                max_tenure_months =
                    EXCLUDED.max_tenure_months,
                min_credit_score =
                    EXCLUDED.min_credit_score,
                max_foir_percent =
                    EXCLUDED.max_foir_percent,
                min_age =
                    EXCLUDED.min_age,
                max_age =
                    EXCLUDED.max_age,
                allowed_employment_types =
                    EXCLUDED.allowed_employment_types;
            """,
            (
                product["product_id"],
                product["product_name"],
                product["description"],
                product["annual_interest_rate"],
                product["min_loan_amount"],
                product["max_loan_amount"],
                product["min_tenure_months"],
                product["max_tenure_months"],
                product["min_credit_score"],
                product["max_foir_percent"],
                product["min_age"],
                product["max_age"],
                product["allowed_employment_types"],
            ),
        )

    return len(products)


def seed_database():
    """
    Seed PostgreSQL with the project's synthetic
    customer and loan product datasets.
    """
    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            customer_count = seed_customers(cursor)
            product_count = seed_loan_products(cursor)

        connection.commit()

    print("Database seeding completed successfully.")
    print(f"Customers seeded: {customer_count}")
    print(f"Loan products seeded: {product_count}")


if __name__ == "__main__":
    seed_database()