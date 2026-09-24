from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


MOCK_ASSESSMENT_RESULT = {
    "application_id": 101,
    "customer_id": "CUS001",
    "product_id": "PERSONAL_FLEXI",
    "requested_amount": 500000,
    "requested_tenure": 60,
    "estimated_emi": 11248.97,
    "foir": 35.76,
    "risk_level": "MEDIUM",
    "risk_points": 1,
    "risk_factors": [
        "Credit score is moderate."
    ],
    "decision": "ELIGIBLE",
    "reasons": [],
    "retrieved_policy": [],
    "advisory": (
        "The customer satisfies the configured "
        "loan eligibility requirements."
    ),
    "next_agent": "end",
    "audit_trail": [],
}


# =========================================================
# BASIC API ENDPOINTS
# =========================================================

def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "service": (
            "Intelligent Credit Advisory System"
        ),
        "status": "running",
        "version": "1.0.0",
    }


def test_health_endpoint_with_redis_available():
    with patch(
        "api.main.test_redis_connection",
        return_value=True,
    ):
        response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "redis": "available",
    }


def test_health_endpoint_with_redis_unavailable():
    with patch(
        "api.main.test_redis_connection",
        return_value=False,
    ):
        response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "redis": "unavailable",
    }


# =========================================================
# LOAN ASSESSMENT ENDPOINT
# =========================================================

def test_assess_endpoint():
    with patch(
        "api.main.run_loan_advisory",
        return_value=MOCK_ASSESSMENT_RESULT,
    ) as mock_workflow, patch(
        "api.main.set_json_cache",
        return_value=True,
    ) as mock_cache:

        response = client.post(
            "/assess",
            json={
                "customer_id": "CUS001",
                "product_id": "PERSONAL_FLEXI",
                "requested_amount": 500000,
                "requested_tenure": 60,
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["application_id"] == 101
    assert result["decision"] == "ELIGIBLE"
    assert result["risk_level"] == "MEDIUM"
    assert result["foir"] == 35.76

    mock_workflow.assert_called_once_with(
        customer_id="CUS001",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000.0,
        requested_tenure=60,
        persist_to_database=True,
    )

    mock_cache.assert_called_once_with(
        "credit_advisory:assessment:101",
        MOCK_ASSESSMENT_RESULT,
        ttl_seconds=3600,
    )


def test_assess_succeeds_when_redis_unavailable():
    with patch(
        "api.main.run_loan_advisory",
        return_value=MOCK_ASSESSMENT_RESULT,
    ), patch(
        "api.main.set_json_cache",
        return_value=False,
    ):

        response = client.post(
            "/assess",
            json={
                "customer_id": "CUS001",
                "product_id": "PERSONAL_FLEXI",
                "requested_amount": 500000,
                "requested_tenure": 60,
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["application_id"] == 101
    assert result["decision"] == "ELIGIBLE"


# =========================================================
# REQUEST VALIDATION
# =========================================================

def test_assess_rejects_invalid_amount():
    response = client.post(
        "/assess",
        json={
            "customer_id": "CUS001",
            "product_id": "PERSONAL_FLEXI",
            "requested_amount": 0,
            "requested_tenure": 60,
        },
    )

    assert response.status_code == 422


def test_assess_rejects_invalid_tenure():
    response = client.post(
        "/assess",
        json={
            "customer_id": "CUS001",
            "product_id": "PERSONAL_FLEXI",
            "requested_amount": 500000,
            "requested_tenure": 0,
        },
    )

    assert response.status_code == 422


# =========================================================
# API ERROR HANDLING
# =========================================================

def test_assess_handles_value_error():
    with patch(
        "api.main.run_loan_advisory",
        side_effect=ValueError(
            "Customer 'INVALID' was not found "
            "in PostgreSQL."
        ),
    ):
        response = client.post(
            "/assess",
            json={
                "customer_id": "INVALID",
                "product_id": "PERSONAL_FLEXI",
                "requested_amount": 500000,
                "requested_tenure": 60,
            },
        )

    assert response.status_code == 400

    assert (
        "Customer 'INVALID' was not found"
        in response.json()["detail"]
    )


def test_assess_handles_internal_error():
    with patch(
        "api.main.run_loan_advisory",
        side_effect=RuntimeError(
            "Unexpected test error"
        ),
    ):
        response = client.post(
            "/assess",
            json={
                "customer_id": "CUS001",
                "product_id": "PERSONAL_FLEXI",
                "requested_amount": 500000,
                "requested_tenure": 60,
            },
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "The loan assessment could not "
            "be completed."
        )
    }


# =========================================================
# REDIS CACHE ENDPOINT
# =========================================================

def test_get_cached_assessment():
    with patch(
        "api.main.get_json_cache",
        return_value=MOCK_ASSESSMENT_RESULT,
    ) as mock_cache:

        response = client.get(
            "/assessments/101/cache"
        )

    assert response.status_code == 200

    assert response.json() == (
        MOCK_ASSESSMENT_RESULT
    )

    mock_cache.assert_called_once_with(
        "credit_advisory:assessment:101"
    )


def test_cached_assessment_not_found():
    with patch(
        "api.main.get_json_cache",
        return_value=None,
    ):

        response = client.get(
            "/assessments/999/cache"
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": (
            "The assessment was not found "
            "in the Redis cache."
        )
    }