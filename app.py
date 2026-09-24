import os

import httpx
import streamlit as st
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================

load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

API_TIMEOUT_SECONDS = 120.0


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Intelligent Credit Advisory System",
    page_icon="💳",
    layout="wide",
)


# =========================================================
# SESSION STATE
# =========================================================

if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None


# =========================================================
# FASTAPI CLIENT FUNCTIONS
# =========================================================

@st.cache_data(ttl=60)
def fetch_customers():
    """
    Retrieve customer data through the FastAPI service.

    Streamlit does not access PostgreSQL directly.
    """

    response = httpx.get(
        f"{API_BASE_URL}/customers",
        timeout=10.0,
    )

    response.raise_for_status()

    payload = response.json()

    return payload["customers"]


@st.cache_data(ttl=60)
def fetch_loan_products():
    """
    Retrieve loan product data through the FastAPI service.

    Streamlit does not access PostgreSQL directly.
    """

    response = httpx.get(
        f"{API_BASE_URL}/loan-products",
        timeout=10.0,
    )

    response.raise_for_status()

    payload = response.json()

    return payload["loan_products"]


def submit_loan_assessment(
    customer_id,
    product_id,
    requested_amount,
    requested_tenure,
):
    """
    Submit a loan assessment request to FastAPI.

    FastAPI invokes the LangGraph workflow and handles
    PostgreSQL persistence and Redis caching.
    """

    response = httpx.post(
        f"{API_BASE_URL}/assess",
        json={
            "customer_id": customer_id,
            "product_id": product_id,
            "requested_amount": requested_amount,
            "requested_tenure": requested_tenure,
        },
        timeout=API_TIMEOUT_SECONDS,
    )

    if response.is_error:

        try:
            error_payload = response.json()
            error_detail = error_payload.get(
                "detail",
                "Unknown API error.",
            )

        except Exception:
            error_detail = response.text

        raise RuntimeError(
            f"FastAPI returned HTTP "
            f"{response.status_code}: "
            f"{error_detail}"
        )

    return response.json()


# =========================================================
# HEADER
# =========================================================

st.title("💳 Intelligent Credit Advisory System")

st.caption(
    "FastAPI-served, LangGraph-orchestrated multi-agent "
    "loan eligibility, affordability, risk analysis, "
    "policy retrieval and AI-powered credit advisory."
)

st.info(
    "Educational prototype only. The results shown by this system "
    "do not represent a formal lending decision by any real bank, "
    "NBFC, financial institution, or regulatory authority."
)


# =========================================================
# MULTI-AGENT ARCHITECTURE
# =========================================================

with st.expander(
    "View System & Multi-Agent Architecture",
    expanded=False,
):

    st.code(
        """
                    Streamlit User Interface
                             |
                             | HTTP
                             v
                         FastAPI
                             |
                             v
                      Supervisor Agent
                             |
                             v
                   Data Retrieval Agent
                             |
                             v
                        Supervisor
                             |
                             v
                     Risk Analysis Agent
                             |
                             v
                        Supervisor
                             |
                             v
                Underwriting Decision Agent
                             |
                             v
                        Supervisor
                             |
                             v
                     Policy / RAG Agent
                             |
                             v
                        Supervisor
                             |
                             v
                    Explanation Agent
                             |
                             v
                        Supervisor
                             |
                             v
                            END

          PostgreSQL + pgvector     Redis Cache
                   ^                    ^
                   |                    |
                   +------ FastAPI -----+
        """,
        language="text",
    )

    st.write(
        "The Streamlit interface communicates with the backend "
        "through FastAPI. Streamlit does not directly invoke the "
        "LangGraph workflow or query PostgreSQL."
    )

    st.write(
        "FastAPI invokes the LangGraph workflow. The Supervisor "
        "Agent inspects the shared workflow state and conditionally "
        "routes execution to the appropriate specialized agent."
    )

    st.write(
        "After each specialized agent completes its task, control "
        "returns to the Supervisor Agent. The Supervisor then "
        "determines which stage should execute next."
    )

    st.write(
        "PostgreSQL acts as the persistent system of record for "
        "customer, product, application and audit data. pgvector "
        "supports semantic policy retrieval, while Redis provides "
        "temporary caching of completed assessments."
    )

    st.write(
        "Financial calculations, risk classification and eligibility "
        "decisions remain deterministic. Gemini is used for policy "
        "embeddings and grounded natural-language explanation."
    )


# =========================================================
# LOAD DATA THROUGH FASTAPI
# =========================================================

try:

    customers = fetch_customers()
    products = fetch_loan_products()

except httpx.ConnectError:

    st.error(
        "The FastAPI backend is not running. "
        "Start the FastAPI server and then refresh this page."
    )

    st.code(
        r".\.venv\Scripts\python.exe -m uvicorn api.main:app --reload",
        language="powershell",
    )

    st.stop()

except httpx.TimeoutException:

    st.error(
        "The FastAPI backend did not respond within the expected "
        "time. Please check that the backend is running correctly."
    )

    st.stop()

except httpx.HTTPStatusError as error:

    st.error(
        "FastAPI could not provide the customer or loan product "
        f"data. HTTP status: {error.response.status_code}"
    )

    st.stop()

except Exception as error:

    st.error(
        "The application could not retrieve data from FastAPI: "
        f"{error}"
    )

    st.stop()


if not customers:

    st.error(
        "No customers were returned by the FastAPI service."
    )

    st.stop()


if not products:

    st.error(
        "No loan products were returned by the FastAPI service."
    )

    st.stop()


customer_options = {
    customer["name"]: customer["customer_id"]
    for customer in customers
}

product_options = {
    product["product_name"]: product["product_id"]
    for product in products
}


# =========================================================
# APPLICATION INPUTS
# =========================================================

st.header("Loan Application")

left_column, right_column = st.columns(2)


with left_column:

    selected_customer_name = st.selectbox(
        "Select Customer",
        options=list(customer_options.keys()),
    )

    requested_amount = st.number_input(
        "Requested Loan Amount (INR)",
        min_value=10000,
        max_value=5000000,
        value=500000,
        step=10000,
    )


with right_column:

    selected_product_name = st.selectbox(
        "Select Loan Product",
        options=list(product_options.keys()),
    )

    requested_tenure = st.number_input(
        "Requested Tenure (Months)",
        min_value=6,
        max_value=120,
        value=60,
        step=6,
    )


selected_customer_id = customer_options[
    selected_customer_name
]

selected_product_id = product_options[
    selected_product_name
]


# Find complete selected customer
selected_customer = next(
    customer
    for customer in customers
    if customer["customer_id"] == selected_customer_id
)


# Find complete selected product
selected_product = next(
    product
    for product in products
    if product["product_id"] == selected_product_id
)


# =========================================================
# CUSTOMER AND PRODUCT INFORMATION
# =========================================================

st.divider()

profile_column, product_column = st.columns(2)


with profile_column:

    st.subheader("Customer Profile")

    st.write(
        f"**Customer ID:** "
        f"{selected_customer['customer_id']}"
    )

    st.write(
        f"**Employment:** "
        f"{selected_customer['employment_type']}"
    )

    st.write(
        f"**Monthly Net Income:** "
        f"₹{selected_customer['monthly_net_income']:,.2f}"
    )

    st.write(
        f"**Existing Monthly Obligations:** "
        f"₹{selected_customer['existing_monthly_obligations']:,.2f}"
    )

    st.write(
        f"**Credit Score:** "
        f"{selected_customer['credit_score']}"
    )

    st.write(
        f"**KYC Status:** "
        f"{selected_customer['kyc_status']}"
    )

    st.write(
        f"**Income Proof Verified:** "
        f"{selected_customer['income_proof_verified']}"
    )


with product_column:

    st.subheader("Loan Product Information")

    st.write(
        f"**Product ID:** "
        f"{selected_product['product_id']}"
    )

    st.write(
        f"**Interest Rate:** "
        f"{selected_product['annual_interest_rate']}% p.a."
    )

    st.write(
        f"**Loan Amount Range:** "
        f"₹{selected_product['min_loan_amount']:,.0f} "
        f"to ₹{selected_product['max_loan_amount']:,.0f}"
    )

    st.write(
        f"**Tenure Range:** "
        f"{selected_product['min_tenure_months']} "
        f"to {selected_product['max_tenure_months']} months"
    )

    st.write(
        f"**Minimum Credit Score:** "
        f"{selected_product['min_credit_score']}"
    )

    st.write(
        f"**Maximum FOIR:** "
        f"{selected_product['max_foir_percent']}%"
    )


# =========================================================
# MULTI-AGENT ASSESSMENT BUTTON
# =========================================================

st.divider()

run_button = st.button(
    "Run Multi-Agent Loan Assessment",
    type="primary",
    use_container_width=True,
)


# =========================================================
# CALL FASTAPI ASSESSMENT ENDPOINT
# =========================================================

if run_button:

    try:

        with st.spinner(
            "Sending the application to FastAPI and running "
            "the supervisor-routed multi-agent credit "
            "advisory workflow..."
        ):

            workflow_result = submit_loan_assessment(
                customer_id=selected_customer_id,
                product_id=selected_product_id,
                requested_amount=requested_amount,
                requested_tenure=requested_tenure,
            )

            st.session_state.workflow_result = (
                workflow_result
            )

    except httpx.ConnectError:

        st.session_state.workflow_result = None

        st.error(
            "The assessment could not be started because "
            "the FastAPI backend is not running."
        )

    except httpx.TimeoutException:

        st.session_state.workflow_result = None

        st.error(
            "The assessment request timed out. The AI explanation "
            "or policy retrieval service may be taking longer than "
            "expected. Please check the FastAPI terminal."
        )

    except Exception as error:

        st.session_state.workflow_result = None

        st.error(
            "The multi-agent workflow could not be completed "
            f"through FastAPI: {error}"
        )


# =========================================================
# DISPLAY WORKFLOW RESULT
# =========================================================

result = st.session_state.workflow_result


if result:

    st.header("Assessment Result")

    application_id = result.get(
        "application_id"
    )

    if application_id is not None:

        st.caption(
            f"Application ID: {application_id} | "
            "Persisted in PostgreSQL"
        )

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Estimated EMI",
            f"₹{result['estimated_emi']:,.2f}",
        )


    with col2:

        st.metric(
            "FOIR",
            f"{result['foir']:.2f}%",
        )


    with col3:

        st.metric(
            "Eligibility",
            result["decision"],
        )


    with col4:

        st.metric(
            "Risk Level",
            result["risk_level"],
        )


    # =====================================================
    # ELIGIBILITY EXPLANATION
    # =====================================================

    st.subheader("Eligibility Explanation")


    if result["reasons"]:

        for reason in result["reasons"]:

            st.warning(
                reason
            )

    else:

        st.success(
            "All configured eligibility checks passed."
        )


    # =====================================================
    # RISK INDICATORS
    # =====================================================

    st.subheader("Risk Indicators")

    st.write(
        f"**Risk Points:** "
        f"{result['risk_points']}"
    )


    if result["risk_factors"]:

        for factor in result["risk_factors"]:

            st.write(
                f"• {factor}"
            )

    else:

        st.success(
            "No additional risk factors were identified "
            "by the prototype risk model."
        )


    # =====================================================
    # AI CREDIT ADVISORY
    # =====================================================

    st.divider()

    st.header("AI Credit Advisory")

    st.write(
        "The Explanation Agent uses the deterministic assessment "
        "together with policy sections retrieved by the Policy / "
        "RAG Agent. The AI does not independently determine "
        "loan eligibility."
    )

    st.markdown(
        result["advisory"]
    )


    # =====================================================
    # RETRIEVED POLICY CONTEXT
    # =====================================================

    with st.expander(
        "View Retrieved Policy Context",
        expanded=False,
    ):

        retrieved_policy = result.get(
            "retrieved_policy",
            [],
        )

        if not retrieved_policy:

            st.info(
                "No policy context was returned for this assessment."
            )

        for index, policy_item in enumerate(
            retrieved_policy,
            start=1,
        ):

            st.markdown(
                f"### Retrieved Policy Section {index}"
            )

            source_title = policy_item.get(
                "source_title"
            )

            source_type = policy_item.get(
                "source_type"
            )

            source_url = policy_item.get(
                "source_url"
            )

            if source_title:

                st.write(
                    f"**Source:** {source_title}"
                )

            if source_type:

                st.write(
                    f"**Source Type:** {source_type}"
                )

            if source_url:

                st.write(
                    f"**Reference URL:** {source_url}"
                )

            similarity = policy_item.get(
                "similarity"
            )

            if similarity is not None:

                st.write(
                    f"**Similarity Score:** "
                    f"{similarity:.4f}"
                )

            st.write(
                policy_item.get(
                    "text",
                    "No policy text available.",
                )
            )

            if index < len(
                retrieved_policy
            ):

                st.divider()


    # =====================================================
    # MULTI-AGENT AUDIT TRAIL
    # =====================================================

    st.divider()

    st.header(
        "Multi-Agent Execution & Audit Trail"
    )

    st.write(
        "The audit trail records both Supervisor routing decisions "
        "and the actions performed by each specialized agent during "
        "the assessment. These events are persisted in PostgreSQL."
    )


    audit_trail = result.get(
        "audit_trail",
        [],
    )


    for index, entry in enumerate(
        audit_trail,
        start=1,
    ):

        with st.expander(
            f"{index}. {entry['agent']}",
            expanded=False,
        ):

            st.write(
                f"**Action:** {entry['action']}"
            )

            details = entry.get(
                "details",
                {},
            )

            if details:

                st.write(
                    "**Recorded Details:**"
                )

                st.json(
                    details
                )


    # =====================================================
    # WORKFLOW COMPLETION
    # =====================================================

    st.divider()

    st.subheader("Workflow Completion")

    completed_agents = list(
        dict.fromkeys(
            entry["agent"]
            for entry in audit_trail
        )
    )

    st.success(
        f"Multi-agent workflow completed successfully "
        f"across {len(completed_agents)} participating agents."
    )

    st.write(
        " → ".join(
            completed_agents
        )
    )

    st.caption(
        f"{len(audit_trail)} total workflow and "
        f"routing events were recorded in the audit trail."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Intelligent Credit Advisory System | "
    "Streamlit + FastAPI + LangGraph Multi-Agent "
    "Educational AI & Financial Technology Prototype"
)