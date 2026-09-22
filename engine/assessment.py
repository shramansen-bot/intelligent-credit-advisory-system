from engine.data_loader import load_customers, load_loan_products
from engine.affordability import calculate_emi, calculate_foir
from engine.eligibility import evaluate_eligibility


def find_customer(customers, customer_id):
    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer

    return None


def find_product(products, product_id):
    for product in products:
        if product["product_id"] == product_id:
            return product

    return None


def assess_loan(
    customer_id,
    product_id,
    requested_amount,
    requested_tenure
):
    customers = load_customers()
    products = load_loan_products()

    customer = find_customer(customers, customer_id)
    product = find_product(products, product_id)

    if customer is None:
        return {
            "error": "Customer not found."
        }

    if product is None:
        return {
            "error": "Loan product not found."
        }

    emi = calculate_emi(
        requested_amount,
        product["annual_interest_rate"],
        requested_tenure
    )

    foir = calculate_foir(
        customer["monthly_net_income"],
        customer["existing_monthly_obligations"],
        emi
    )

    eligibility = evaluate_eligibility(
        customer,
        product,
        requested_amount,
        requested_tenure,
        foir
    )

    return {
        "customer_name": customer["name"],
        "product_name": product["product_name"],
        "requested_amount": requested_amount,
        "requested_tenure": requested_tenure,
        "estimated_emi": emi,
        "foir": foir,
        "decision": eligibility["decision"],
        "reasons": eligibility["reasons"]
    }


if __name__ == "__main__":
    result = assess_loan(
        customer_id="CUS003",
        product_id="PERSONAL_FLEXI",
        requested_amount=500000,
        requested_tenure=60
    )

    print(result)