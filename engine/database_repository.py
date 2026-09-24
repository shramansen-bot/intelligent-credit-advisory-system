from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from engine.database import get_database_connection


# =========================================================
# DATA NORMALIZATION HELPERS
# =========================================================

def normalize_customer(customer):
    """
    Convert a PostgreSQL customer row into the dictionary
    format expected by the application.
    """

    if customer is None:
        return None

    customer = dict(customer)

    customer["fraud_flag"] = customer.pop(
        "fraud_review_flag"
    )

    customer["monthly_net_income"] = float(
        customer["monthly_net_income"]
    )

    customer["existing_monthly_obligations"] = float(
        customer["existing_monthly_obligations"]
    )

    customer["monthly_expenses"] = float(
        customer["monthly_expenses"]
    )

    customer["employment_years"] = float(
        customer["employment_years"]
    )

    return customer


def normalize_loan_product(product):
    """
    Convert a PostgreSQL loan-product row into the
    dictionary format expected by the application.
    """

    if product is None:
        return None

    product = dict(product)

    product["annual_interest_rate"] = float(
        product["annual_interest_rate"]
    )

    product["min_loan_amount"] = float(
        product["min_loan_amount"]
    )

    product["max_loan_amount"] = float(
        product["max_loan_amount"]
    )

    product["max_foir_percent"] = float(
        product["max_foir_percent"]
    )

    return product


# =========================================================
# CUSTOMER RETRIEVAL
# =========================================================

def get_customer_by_id(customer_id):
    """
    Retrieve a single customer from PostgreSQL.

    Returns:
        dict: Customer data if found.
        None: If no matching customer exists.
    """

    query = """
        SELECT
            customer_id,
            name,
            age,
            employment_type,
            monthly_net_income,
            existing_monthly_obligations,
            monthly_expenses,
            credit_score,
            kyc_status,
            income_proof_verified,
            employment_years,
            fraud_review_flag
        FROM customers
        WHERE customer_id = %s;
    """

    with get_database_connection() as connection:
        with connection.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(
                query,
                (customer_id,),
            )

            customer = cursor.fetchone()

    return normalize_customer(
        customer
    )


def get_all_customers():
    """
    Retrieve all customers from PostgreSQL.

    Results are ordered by customer name so that API and
    Streamlit selection lists remain predictable.
    """

    query = """
        SELECT
            customer_id,
            name,
            age,
            employment_type,
            monthly_net_income,
            existing_monthly_obligations,
            monthly_expenses,
            credit_score,
            kyc_status,
            income_proof_verified,
            employment_years,
            fraud_review_flag
        FROM customers
        ORDER BY name;
    """

    with get_database_connection() as connection:
        with connection.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(query)
            customers = cursor.fetchall()

    return [
        normalize_customer(customer)
        for customer in customers
    ]


# =========================================================
# LOAN PRODUCT RETRIEVAL
# =========================================================

def get_loan_product_by_id(product_id):
    """
    Retrieve a single loan product from PostgreSQL.

    Returns:
        dict: Loan product data if found.
        None: If no matching product exists.
    """

    query = """
        SELECT
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
        FROM loan_products
        WHERE product_id = %s;
    """

    with get_database_connection() as connection:
        with connection.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(
                query,
                (product_id,),
            )

            product = cursor.fetchone()

    return normalize_loan_product(
        product
    )


def get_all_loan_products():
    """
    Retrieve all loan products from PostgreSQL.

    Results are ordered by product name so that API and
    Streamlit selection lists remain predictable.
    """

    query = """
        SELECT
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
        FROM loan_products
        ORDER BY product_name;
    """

    with get_database_connection() as connection:
        with connection.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(query)
            products = cursor.fetchall()

    return [
        normalize_loan_product(product)
        for product in products
    ]


# =========================================================
# CREATE LOAN APPLICATION
# =========================================================

def create_loan_application(
    customer_id,
    product_id,
    requested_amount,
    requested_tenure,
):
    """
    Create a new loan application in PostgreSQL.

    A newly created application starts with the
    SUBMITTED status.

    Returns:
        int: Newly generated application ID.
    """

    query = """
        INSERT INTO loan_applications (
            customer_id,
            product_id,
            requested_amount,
            requested_tenure,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING application_id;
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    customer_id,
                    product_id,
                    requested_amount,
                    requested_tenure,
                    "SUBMITTED",
                ),
            )

            application_id = (
                cursor.fetchone()[0]
            )

        connection.commit()

    return application_id


# =========================================================
# UPDATE LOAN APPLICATION
# =========================================================

def update_loan_application_result(
    application_id,
    estimated_emi,
    foir,
    risk_level,
    risk_points,
    decision,
):
    """
    Update an existing loan application with the final
    assessment produced by the multi-agent workflow.

    The status is changed from SUBMITTED to COMPLETED.
    """

    query = """
        UPDATE loan_applications
        SET
            estimated_emi = %s,
            foir = %s,
            risk_level = %s,
            risk_points = %s,
            decision = %s,
            status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE application_id = %s;
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    estimated_emi,
                    foir,
                    risk_level,
                    risk_points,
                    decision,
                    "COMPLETED",
                    application_id,
                ),
            )

        connection.commit()


# =========================================================
# SAVE AUDIT TRAIL
# =========================================================

def save_audit_logs(
    application_id,
    audit_trail,
):
    """
    Persist every Supervisor and agent audit event generated
    during the LangGraph workflow into PostgreSQL.

    The details dictionary is stored in PostgreSQL as JSONB.
    """

    query = """
        INSERT INTO audit_logs (
            application_id,
            agent_name,
            action,
            details
        )
        VALUES (%s, %s, %s, %s);
    """

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            for audit_entry in audit_trail:
                cursor.execute(
                    query,
                    (
                        application_id,
                        audit_entry["agent"],
                        audit_entry["action"],
                        Jsonb(
                            audit_entry.get(
                                "details",
                                {},
                            )
                        ),
                    ),
                )

        connection.commit()