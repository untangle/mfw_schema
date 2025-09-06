# mfw_schema
Untangle MicroFirewall JSON schema

This stores the JSON schemas that describe the settings.

[Online Documentation](https://microfirewall.readthedocs.io/en/latest/?)

## Getting Started

### Prerequisites

- Python 3.6+

### Setup

1.  **Create a virtual environment:**

    ```bash
    python3 -m venv venv
    ```

2.  **Activate the virtual environment:**

    -   **On Windows:**

        ```bash
        .\\venv\\Scripts\\activate
        ```

    -   **On macOS and Linux:**

        ```bash
        source venv/bin/activate
        ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running the validation tests

You can run the validation tests in a few ways:

1.  **Run all tests using the VS Code task:**
    -   Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
    -   Type "Tasks: Run Test Task".
    -   Select "Run All Validations".

2.  **Run individual validation scripts:**
    -   To run a specific validation test, you can execute any of the `validate_*.py` scripts located in the `v1` subdirectories. For example, to validate the accounts schema, you can run the following command:

    ```bash
    python3 v1/accounts/validate_accounts.py
    ```

### Generating the Pydantic models

To generate the Pydantic models, you can run the `generate_models.sh` script:

```bash
./generate_models.sh
