from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.workflow import run_loan_advisory
from engine.database_repository import (
    get_all_customers,
    get_all_loan_products,
)
from engine.redis_client import (
    get_json_cache,
    set_json_cache,
    test_redis_connection,
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Intelligent Credit Advisory System API",
    description=(
        "FastAPI service for the LangGraph-based "
        "multi-agent Intelligent Credit Advisory System."
    ),
    version="1.0.0",
)


# =========================================================
# REDIS CONFIGURATION
# =========================================================

ASSESSMENT_CACHE_TTL_SECONDS = 3600


def build_assessment_cache_key(application_id):
    """
    Build the Redis key used for a completed assessment.
    """

    return (
        "credit_advisory:"
        f"assessment:{application_id}"
    )


# =========================================================
# REQUEST MODEL
# =========================================================

class LoanAssessmentRequest(BaseModel):
    """
    Input required to run a loan assessment.
    """

    customer_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Existing customer ID stored in PostgreSQL."
        ),
        examples=["CUS001"],
    )

    product_id: str = Field(
        ...,
        min_length=1,
        description=(
            "Loan product ID stored in PostgreSQL."
        ),
        examples=["PERSONAL_FLEXI"],
    )

    requested_amount: float = Field(
        ...,
        gt=0,
        description="Requested loan amount.",
        examples=[500000],
    )

    requested_tenure: int = Field(
        ...,
        gt=0,
        description=(
            "Requested loan tenure in months."
        ),
        examples=[60],
    )


# =========================================================
# BASIC ENDPOINTS
# =========================================================

@app.get("/")
def root():
    """
    Basic API information endpoint.
    """

    return {
        "service": (
            "Intelligent Credit Advisory System"
        ),
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    """
    Report API health and Redis availability.

    Redis is optional for core loan processing, so the API
    remains healthy even when Redis is unavailable.
    """

    redis_available = (
        test_redis_connection()
    )

    return {
        "status": "healthy",
        "redis": (
            "available"
            if redis_available
            else "unavailable"
        ),
    }


# =========================================================
# CUSTOMER ENDPOINT
# =========================================================

@app.get("/customers")
def list_customers():
    """
    Retrieve all available customers from PostgreSQL.
    """

    try:
        customers = get_all_customers()

        return {
            "customers": customers,
            "count": len(customers),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Customer data could not "
                "be retrieved."
            ),
        ) from error


# =========================================================
# LOAN PRODUCT ENDPOINT
# =========================================================

@app.get("/loan-products")
def list_loan_products():
    """
    Retrieve all available loan products from PostgreSQL.
    """

    try:
        products = get_all_loan_products()

        return {
            "loan_products": products,
            "count": len(products),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Loan product data could not "
                "be retrieved."
            ),
        ) from error


# =========================================================
# LOAN ASSESSMENT ENDPOINT
# =========================================================

@app.post("/assess")
def assess_loan(
    request: LoanAssessmentRequest,
):
    """
    Run the complete LangGraph multi-agent credit
    advisory workflow.

    PostgreSQL remains the permanent system of record.

    After a successful assessment, Redis stores a temporary
    copy of the result for fast recent-result retrieval.

    Redis failure does not prevent the assessment from
    completing.
    """

    try:
        result = run_loan_advisory(
            customer_id=request.customer_id,
            product_id=request.product_id,
            requested_amount=(
                request.requested_amount
            ),
            requested_tenure=(
                request.requested_tenure
            ),
            persist_to_database=True,
        )

        application_id = result.get(
            "application_id"
        )

        if application_id is not None:
            cache_key = (
                build_assessment_cache_key(
                    application_id
                )
            )

            set_json_cache(
                cache_key,
                result,
                ttl_seconds=(
                    ASSESSMENT_CACHE_TTL_SECONDS
                ),
            )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "The loan assessment could not "
                "be completed."
            ),
        ) from error


# =========================================================
# RECENT ASSESSMENT CACHE ENDPOINT
# =========================================================

@app.get(
    "/assessments/{application_id}/cache"
)
def get_cached_assessment(
    application_id: int,
):
    """
    Retrieve a recently completed assessment from Redis.

    Cached assessments expire automatically after the
    configured TTL.

    PostgreSQL remains the permanent source of record.
    """

    cache_key = build_assessment_cache_key(
        application_id
    )

    cached_result = get_json_cache(
        cache_key
    )

    if cached_result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "The assessment was not found "
                "in the Redis cache."
            ),
        )

    return cached_result