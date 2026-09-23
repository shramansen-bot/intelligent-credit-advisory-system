# Intelligent Credit Advisory System

An AI-powered credit assessment and loan advisory prototype that combines deterministic financial calculations, rule-based eligibility checks, risk assessment, semantic policy retrieval, and grounded Generative AI explanations.

The application provides an explainable loan assessment through an interactive Streamlit interface.

> **Disclaimer:** This project is an educational prototype. The customer records, loan products, lending policies, thresholds, and assessment rules used in this repository are synthetic and do not represent the policies of any real bank, NBFC, financial institution, or regulatory authority.

---

## 1. Project Overview

Loan assessment involves multiple factors such as affordability, credit profile, customer verification, product-specific eligibility rules, and risk indicators.

This project demonstrates how these factors can be combined into an explainable credit advisory workflow.

The system performs the core financial assessment using deterministic Python logic and uses Generative AI only to explain the calculated result.

This separation ensures that the AI model does not independently decide whether a loan applicant is eligible.

The system includes:

- EMI calculation
- FOIR calculation
- Product-specific eligibility checking
- Explainable rejection reasons
- Risk classification
- Synthetic lending-policy knowledge base
- Embedding-based semantic policy retrieval
- Gemini-powered grounded advisory generation
- Interactive Streamlit user interface
- Automated unit testing

---

## 2. Problem Statement and Solution Approach

Traditional loan assessment involves evaluating several financial and non-financial conditions. A useful advisory system should not only provide an eligibility result but should also explain the factors contributing to that result.

The Intelligent Credit Advisory System addresses this by separating the workflow into two major layers.

### Deterministic Assessment Layer

Python modules calculate and evaluate:

- EMI
- Fixed Obligation to Income Ratio (FOIR)
- Credit-score requirements
- KYC status
- Income-proof verification
- Employment-type eligibility
- Fraud-review flag
- Loan-amount limits
- Loan-tenure limits
- Risk indicators

These rules produce the actual assessment result.

### AI Advisory Layer

The system retrieves relevant sections from a synthetic lending-policy knowledge base using semantic embeddings.

The retrieved policy context and deterministic assessment are then supplied to Gemini, which generates a user-friendly explanation.

The AI layer is explicitly instructed not to modify or override the calculated eligibility decision, EMI, FOIR, risk points, or risk classification.

---

## 3. Key Features

### Explainable Loan Eligibility

Instead of returning only `ELIGIBLE` or `NOT ELIGIBLE`, the system identifies the specific rules that failed.

Example:

```text
Credit score is below the minimum requirement.
FOIR exceeds the maximum permitted limit.
```

### Affordability Analysis

The system includes functionality for:

- Estimated monthly EMI
- FOIR
- Disposable income
- Maximum affordable EMI

### Risk Assessment

A separate prototype risk model classifies applications as:

- LOW
- MEDIUM
- HIGH

Risk classification and eligibility are deliberately kept separate.

### Retrieval-Augmented Generation (RAG)

Relevant policy sections are retrieved from the synthetic lending-policy knowledge base using semantic embeddings.

This context is supplied to the Generative AI model to produce a grounded explanation.

### Persistent Embedding Cache

Policy embeddings are stored locally after initial generation so that they do not need to be regenerated every time the application starts.

The generated vector cache is excluded from Git and can be rebuilt automatically.

### Interactive Streamlit Interface

Users can:

- Select a synthetic customer
- Select a loan product
- Enter the requested loan amount
- Select the loan tenure
- Run the deterministic assessment
- View EMI, FOIR, eligibility, and risk
- View detailed eligibility reasons
- Generate an AI-powered advisory

---

## 4. System Architecture

```text
Customer Data + Loan Product Data
               |
               v
      Deterministic Assessment
        /        |        \
       v         v         v
      EMI       FOIR    Eligibility
                         Checks
               |
               v
         Risk Assessment
               |
               v
      Structured Assessment
          /             \
         v               v
  Streamlit UI     Policy Retrieval
                         |
                         v
                  Policy Knowledge Base
                         |
                         v
                  Gemini Embeddings
                         |
                         v
               Relevant Policy Context
                         |
                         v
                    Gemini LLM
                         |
                         v
               Grounded AI Advisory
                         |
                         v
                    Streamlit UI
```

### Design Principle

The Generative AI model is **not the decision engine**.

Eligibility, EMI, FOIR, and risk calculations are performed using deterministic Python logic.

Gemini is used to explain the resulting assessment with relevant retrieved policy context.

---

## 5. Project Structure

```text
intelligent-credit-advisory-system/
|
|-- app.py
|
|-- data/
|   |-- customers.json
|   `-- loan_products.json
|
|-- engine/
|   |-- __init__.py
|   |-- affordability.py
|   |-- assessment.py
|   |-- data_loader.py
|   |-- eligibility.py
|   |-- risk.py
|   |-- ai_advisor.py
|   |-- policy_loader.py
|   `-- policy_retriever.py
|
|-- knowledge_base/
|   `-- lending_policy.txt
|
|-- tests/
|   |-- test_affordability.py
|   |-- test_assessment.py
|   |-- test_risk.py
|   `-- test_ai_advisor.py
|
|-- vector_store/
|   `-- policy_embeddings.json
|
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md
```

`vector_store/policy_embeddings.json` is generated locally and is intentionally excluded from version control.

---

## 6. Technology Stack

- Python
- Streamlit
- Google Gemini API
- Google GenAI Python SDK
- Gemini Embeddings
- Pytest
- python-dotenv
- JSON
- Git
- GitHub

---

## 7. Prerequisites

Before running the project, ensure that the following are installed:

- Python
- Git
- pip
- A Google Gemini API key for RAG and AI advisory functionality

A Python virtual environment is recommended.

---

## 8. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/shramansen-bot/intelligent-credit-advisory-system.git
```

Move into the project directory:

```bash
cd intelligent-credit-advisory-system
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

> **PowerShell note:** On some Windows systems, the execution policy may prevent `Activate.ps1` from running. The project can still be used without changing the system execution policy. In that case, use the Python executable inside the virtual environment directly.

Install dependencies without activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the automated tests without activation:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run the Streamlit application without activation:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

#### macOS/Linux

```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

If the virtual environment has been activated, run:

```bash
python -m pip install -r requirements.txt
```

---

## 9. Environment Configuration

The project uses an environment variable for the Gemini API key.

A template is provided in:

```text
.env.example
```

Create a new `.env` file in the project root.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with a valid Gemini API key.

### Important

A Gemini API key is required when the application needs to:

- Generate policy embeddings
- Generate query embeddings
- Retrieve policy context using semantic embeddings
- Generate the AI Credit Advisory

The deterministic Python modules and mocked automated tests do not require a live Gemini API key.

### Security

The actual `.env` file must never be committed to GitHub.

The repository's `.gitignore` excludes `.env`.

Only `.env.example`, which contains no real secret, should be committed.

---

## 10. Running the Application

With the virtual environment activated, run:

```bash
streamlit run app.py
```

If PowerShell activation is unavailable, run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit will start the local application, normally at:

```text
http://localhost:8501
```

Open the address shown by Streamlit in a web browser.

---

## 11. Application Workflow

1. Select a synthetic customer.
2. Select a loan product.
3. Enter the requested loan amount.
4. Select the requested tenure.
5. Click **Assess Loan**.
6. The deterministic engine calculates EMI and FOIR.
7. Product-specific eligibility checks are performed.
8. Risk indicators and risk classification are calculated.
9. The result is displayed in the Streamlit interface.
10. The user can request an AI Credit Advisory.
11. Relevant synthetic policy sections are retrieved using semantic embeddings.
12. The retrieved context and calculated assessment are sent to Gemini.
13. Gemini generates a grounded explanation of the existing assessment.

---

## 12. Eligibility Checks

The prototype evaluates conditions including:

- Customer age
- Credit score
- Employment type
- KYC verification
- Income-proof verification
- Fraud-review flag
- Requested loan amount
- Requested tenure
- FOIR

An applicant is classified as `ELIGIBLE` only when all applicable eligibility checks pass.

If one or more checks fail, the system returns `NOT ELIGIBLE` together with the corresponding reasons.

---

## 13. Affordability Calculation

### EMI

The application calculates the estimated EMI using the standard reducing-balance loan formula.

### FOIR

For this prototype:

```text
FOIR =
(Existing Monthly Obligations + Proposed Loan EMI)
--------------------------------------------------
               Monthly Net Income
                        x 100
```

The calculated FOIR is compared with the maximum FOIR configured for the selected synthetic loan product.

---

## 14. Risk Assessment

Risk assessment is separate from eligibility.

The prototype assigns risk points based on configured credit-score and FOIR thresholds.

The resulting classifications are:

```text
0 points       -> LOW
1 to 2 points  -> MEDIUM
3+ points      -> HIGH
```

A risk classification does not independently determine eligibility.

These thresholds are synthetic and are used only for demonstration.

---

## 15. RAG and Policy Retrieval

The project uses a lightweight Retrieval-Augmented Generation workflow.

The synthetic policy document is stored at:

```text
knowledge_base/lending_policy.txt
```

The retrieval workflow is:

```text
Policy Document
      |
      v
Section-Based Chunking
      |
      v
Gemini Document Embeddings
      |
      v
Local Embedding Index
      |
      v
Assessment-Based Retrieval Query
      |
      v
Gemini Query Embedding
      |
      v
Cosine Similarity
      |
      v
Top Relevant Policy Sections
      |
      v
Gemini Advisory Prompt
```

Document embeddings use the Gemini embedding service.

Cosine similarity is used to compare the assessment-based query embedding with the policy-section embeddings and identify relevant policy context.

### Local Embedding Cache

When policy embeddings are generated, they are saved locally to:

```text
vector_store/policy_embeddings.json
```

This file is generated automatically and is excluded from GitHub through `.gitignore`.

If the cache does not exist, the system generates a new policy embedding index when retrieval is first required.

---

## 16. AI Grounding and Safety

The AI advisory prompt restricts the model to information supplied by:

1. The deterministic loan assessment.
2. The retrieved synthetic policy context.

The AI is instructed not to:

- Change the eligibility result
- Recalculate or modify EMI
- Recalculate or modify FOIR
- Change risk points
- Change the risk level
- Invent eligibility reasons
- Introduce unsupported lending policies
- Introduce unsupported regulatory requirements

This architecture keeps financial calculations and eligibility decisions deterministic while using Generative AI primarily for explanation.

---

## 17. Lazy Gemini Initialization

Gemini clients are initialized only when Gemini functionality is actually required.

Importing the project's modules does not require a Gemini API key.

This design allows deterministic modules and mocked automated tests to operate without connecting to the external Gemini service.

When an embedding or live AI advisory is requested, the application checks for `GEMINI_API_KEY` and creates the required Gemini client.

---

## 18. Testing

The project includes automated tests using `pytest`.

Run the tests from the project root using:

```bash
python -m pytest
```

On Windows PowerShell systems where virtual-environment activation is blocked, use:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The test suite covers:

- EMI calculation
- FOIR calculation
- Disposable-income calculation
- Maximum-affordable-EMI calculation
- Eligible applications
- Ineligible applications
- Invalid customer handling
- Invalid product handling
- LOW risk classification
- MEDIUM risk classification
- HIGH risk classification
- AI advisory integration logic using mocked external components

The AI unit test mocks both policy retrieval and Gemini generation.

Therefore, running the automated test suite does not require a live Gemini request or API key.

Expected result:

```text
12 passed
```

---

## 19. Synthetic Data

All customer profiles in:

```text
data/customers.json
```

are fictional.

All loan products in:

```text
data/loan_products.json
```

are synthetic.

The lending policy in:

```text
knowledge_base/lending_policy.txt
```

was created specifically for this educational prototype.

The project must not be interpreted as representing actual lending criteria used by a real financial institution.

---

## 20. External Services

### Google Gemini API

The project uses Google's Gemini services for:

- Text embeddings for semantic policy retrieval
- Generative AI advisory explanations

A valid API key must be supplied through the `GEMINI_API_KEY` environment variable when these capabilities are used.

External Gemini calls are not required for the deterministic assessment engine or the mocked automated test suite.

---

## 21. Error Handling

If the Gemini service is temporarily unavailable because of high demand, the AI advisory layer handles the service error and informs the user that the advisory is temporarily unavailable.

The deterministic assessment result remains separate from the availability of the Generative AI service.

If the Gemini API key is missing when Gemini functionality is requested, the system reports that the key must be configured using `.env.example`.

---

## 22. Known Limitations

- The project uses synthetic customers, products, and lending rules.
- It is not connected to a real banking core system or credit bureau.
- It does not perform real KYC or fraud verification.
- Gemini functionality depends on an external API service and internet connectivity.
- AI responses may be temporarily unavailable during API errors or high service demand.
- The locally cached policy embeddings are not automatically invalidated when the policy document is modified.
- The risk model is intentionally simplified for demonstration.
- Semantic retrieval may not always retrieve every policy section relevant to a broad assessment.
- The application currently uses predefined synthetic customer profiles and loan products.
- The system is not intended for real lending decisions.

---

## 23. Future Enhancements

Possible extensions include:

- Automatic embedding-cache invalidation when policy documents change
- Support for multiple policy documents
- More advanced vector-database integration
- Expanded automated testing for policy retrieval
- More detailed affordability analysis
- Additional loan products
- User-entered applicant profiles
- Authentication and role-based access
- Audit logging
- Explainability dashboards
- API-based architecture
- Cloud deployment
- Enhanced retrieval strategies
- Additional error handling and observability

---

## 24. Responsible Use

This application demonstrates how deterministic financial logic and Generative AI can work together while keeping the core assessment explainable.

It is intended exclusively for educational and demonstration purposes.

It should not be used to approve, reject, price, or otherwise make real-world lending decisions.