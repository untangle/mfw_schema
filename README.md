# mfw_schema
Untangle MicroFirewall JSON schema

This stores the JSON schemas that describe the settings.

[Online Documentation](https://microfirewall.readthedocs.io/en/latest/?)

## Getting Started

### Prerequisites

- Python 3.9+

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
```

### Using the Generated Code in Another Project (Git Submodule)

To use the generated Pydantic models in another project, you can add this repository as a Git submodule. This will link the two projects and allow you to keep the schema and generated models in sync.

1.  **Add the submodule:** In your other project's root directory, run the following command:

    ```bash
    git submodule add <repository_url> mfw_schema
    ```

2.  **Initialize the submodule:**

    ```bash
    git submodule update --init --recursive
    ```

3.  **Add the submodule to your Python path:** In your other project, you will need to add the `mfw_schema` directory to your Python path. You can do this by adding the following code to your project's main entry point:

    ```python
    import sys
    sys.path.append("path/to/mfw_schema")
    ```

4.  **Import the generated models:** You can now import the generated models in your other project:

    ```python
    from pydantic_models.v1_config import V1Config
    ```

### Adding a New Object to the Schema

To add a new object to the schema, you will need to perform the following steps:

1.  **Create a new directory:** Create a new directory for your object in the `v1` directory. For example, if you are adding a "widgets" object, you would create the directory `v1/widgets`.

2.  **Create the schema file:** Inside your new directory, create a `widgets_schema.json` file. This file will contain the JSON schema for your new object.

3.  **Create the test file:** Create a `test_widgets.json` file in the same directory. This file will contain sample data that can be used to validate your schema.

4.  **Create the validation script:** Create a `validate_widgets.py` script in the same directory. This script will contain the validation tests for your new object. You can use one of the existing validation scripts as a template.

5.  **Update the main schema file:** Add a reference to your new schema in the `v1/schema.json` file. For example:

    ```json
    "widgets": {
        "$ref": "widgets/widgets_schema.json#/definitions/widgets_settings"
    }
    ```

6.  **Update the main validation script:** Add your new validation script to the `validate_dict` in the `validate.py` file. For example:

    ```python
    "widgets_schema": validate_widgets,
    ```

7.  **Run the validation tests:** Run the `validate.py` script to ensure that your new schema is valid and that all tests pass.

8.  **Generate the Pydantic models:** Run the `generate_models.sh` script to generate the updated Pydantic models.

