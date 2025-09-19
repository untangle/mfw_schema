import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError


def validate_all_schemas(directory: Path) -> None:
    """
    Validates all JSON files in a directory to ensure they are valid JSON Schemas.
    """
    error_found = False
    for json_file in sorted(directory.rglob("*.json")):
        print(f"Checking: {json_file.relative_to(directory.parent)}...")
        try:
            with open(json_file) as f:
                schema_data = json.load(f)
                # This function specifically checks if the schema *itself* is valid
                Draft7Validator.check_schema(schema_data)
        except json.JSONDecodeError as e:
            print(f"\n--- ERROR: Invalid JSON in file: {json_file} ---")
            print(f"    {e}\n")
            error_found = True
        except SchemaError as e:
            print(f"\n--- ERROR: Invalid Schema structure in file: {json_file} ---")
            # Provide a more helpful error message pointing to the likely cause
            if "is not of type 'string', 'array'" in str(e) and "on key 'type'" in str(e):
                print(
                    "    This often means a property is incorrectly nested under a 'type' keyword."
                )
                print(
                    "    The 'type' keyword value must be a string (e.g., \"object\") or a list of strings."
                )
                print(
                    "    Check for structures like: \"'type': {'type': 'string', ...}\" which are invalid."
                )
            print(f"    Details: {e.message}\n")
            error_found = True
        except Exception as e:  # noqa: BLE001
            print(f"\n--- UNEXPECTED ERROR in file: {json_file} ---")
            print(f"    {e}\n")
            error_found = True

    if error_found:
        print("Schema validation failed. Please fix the errors listed above.")
        sys.exit(1)
    else:
        print("\nAll schemas are structurally valid.")


if __name__ == "__main__":
    if len(sys.argv) < 2:  # noqa: PLR2004
        print("Usage: python validate_schemas.py <directory_to_scan>")
        sys.exit(1)

    schema_dir = Path(sys.argv[1])
    if not schema_dir.is_dir():
        print(f"Error: Directory not found at '{schema_dir}'")
        sys.exit(1)

    validate_all_schemas(schema_dir)
