#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
SOURCE_SCHEMA_DIR="v1"
TEMP_SCHEMA_DIR="temp_schema_for_codegen"
TOP_LEVEL_SCHEMA_NAME="schema.json"
OUTPUT_FILE="pydantic_models/v1_config.py"
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
CLASS_NAME="V1Config"

# --- Script Logic ---

# 1. Create a clean temporary directory and copy schemas
echo "Setting up temporary schema directory..."
rm -rf "$TEMP_SCHEMA_DIR" "$OUTPUT_DIR"
mkdir -p "$TEMP_SCHEMA_DIR" "$OUTPUT_DIR"
cp -r "$SOURCE_SCHEMA_DIR"/* "$TEMP_SCHEMA_DIR/"

# 2. Pre-process: Remove all "file:" prefixes from $ref values in the temp directory
echo "Cleaning 'file:' prefixes from schema references..."
find "$TEMP_SCHEMA_DIR" -type f -name "*.json" -print0 | xargs -0 sed -i 's/"\$ref": "file:\([^"]*\)"/"\$ref": "\1"/g'

# 3. Validate the cleaned schemas to find structural errors before generation
echo -e "\n--- Validating all schemas ---"
python3 validate_schemas.py "$TEMP_SCHEMA_DIR"
echo -e "--- Validation Complete ---\n"


# 4. Generate the Pydantic model from the CLEANED and VALIDATED schema
echo "Generating Pydantic model from the cleaned schema..."
datamodel-codegen \
  --input "$TEMP_SCHEMA_DIR/$TOP_LEVEL_SCHEMA_NAME" \
  --input-file-type jsonschema \
  --output "$OUTPUT_FILE" \
  --class-name "$CLASS_NAME" \
  --collapse-root-models \
  --output-model-type pydantic_v2.BaseModel

# 5. Post-process: Remove incorrect relative imports and replace aliases
echo "Fixing generated model..."
sed -i '/from \. import Chain as Chain_1/d' "$OUTPUT_FILE"
sed -i '/from \. import Rule as Rule_1/d' "$OUTPUT_FILE"
sed -i '/from \. import Table as Table_1/d' "$OUTPUT_FILE"
sed -i 's/Rule_1/Rule/g' "$OUTPUT_FILE"
sed -i 's/Chain_1/Chain/g' "$OUTPUT_FILE"
sed -i 's/Table_1/Table/g' "$OUTPUT_FILE"

# 6. Validate the generated model
echo "Validating generated model..."
.venv/bin/python3 test_pydantic_model.py

# 7. Clean up the temporary directory
echo "Cleaning up temporary directory..."
rm -rf "$TEMP_SCHEMA_DIR"

echo "Done! Model saved to $OUTPUT_FILE"
