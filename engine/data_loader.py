import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_customers():
    file_path = DATA_DIR / "customers.json"

    with open(file_path, "r", encoding="utf-8") as file:
        customers = json.load(file)

    return customers


def load_loan_products():
    file_path = DATA_DIR / "loan_products.json"

    with open(file_path, "r", encoding="utf-8") as file:
        products = json.load(file)

    return products


if __name__ == "__main__":
    customers = load_customers()
    products = load_loan_products()

    print("Customers loaded:", len(customers))
    print("Loan products loaded:", len(products))