from engine.assessment import assess_loan


def test_eligible_customer():
    result = assess_loan(
        customer_id="CUS001",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000,
        requested_tenure=60
    )

    assert result["decision"] == "ELIGIBLE"
    assert result["reasons"] == []


def test_ineligible_customer():
    result = assess_loan(
        customer_id="CUS003",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000,
        requested_tenure=60
    )

    assert result["decision"] == "NOT ELIGIBLE"

    assert "Credit score is below the minimum requirement." in result["reasons"]
    assert "FOIR exceeds the maximum permitted limit." in result["reasons"]


def test_customer_not_found():
    result = assess_loan(
        customer_id="INVALID_CUSTOMER",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000,
        requested_tenure=60
    )

    assert result["error"] == "Customer not found."


def test_product_not_found():
    result = assess_loan(
        customer_id="CUS001",
        product_id="INVALID_PRODUCT",
        requested_amount=500000,
        requested_tenure=60
    )

    assert result["error"] == "Loan product not found."