#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
SOURCE_SCHEMA_DIR="v1"
TOP_LEVEL_SCHEMA_NAME="schema.json"
OUTPUT_FILE="pydantic_models/v1_config.py"
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
CLASS_NAME="V1Config"

# --- Script Logic ---

# 1. Create a clean output directory
echo "Setting up output directory..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
# create init file to make this a module for imports
touch "$OUTPUT_DIR/__init__.py"

# 2. Validate the schemas to find structural errors before generation
echo -e "\n--- Validating all schemas ---"
python3 validate_schemas.py "$SOURCE_SCHEMA_DIR"
echo -e "--- Validation Complete ---\n"

# 3. Generate the Pydantic model from the schema
echo "Generating Pydantic model from the schema..."
datamodel-codegen \
  --input "$SOURCE_SCHEMA_DIR/$TOP_LEVEL_SCHEMA_NAME" \
  --input-file-type jsonschema \
  --output "$OUTPUT_FILE" \
  --class-name "$CLASS_NAME" \
  --collapse-root-models \
  --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.9

# 4. Post-process: Remove incorrect relative imports and replace aliases
echo "Fixing generated model..."
sed -i '/from \. import Chain as Chain_1/d' "$OUTPUT_FILE"
sed -i '/from \. import Rule as Rule_1/d' "$OUTPUT_FILE"
sed -i '/from \. import Table as Table_1/d' "$OUTPUT_FILE"
sed -i 's/Rule_1/Rule/g' "$OUTPUT_FILE"
sed -i 's/Chain_1/Chain/g' "$OUTPUT_FILE"
sed -i 's/Table_1/Table/g' "$OUTPUT_FILE"

echo "Ruff Formatting $OUTPUT_DIR"
ruff format "$OUTPUT_DIR"

# 5. Validate the generated model
echo "Validating generated model..."
python3 test_pydantic_model.py

echo "Done! Model saved to $OUTPUT_FILE"
