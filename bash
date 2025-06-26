#!/bin/bash

# ==============================================================================
# 3scale Backend and Product Creation Script (No JQ)
#
# This script automates the creation of a new backend, a new product,
# and associates the backend with the product in Red Hat 3scale using the
# 3scale Admin REST API.
#
# This version does NOT require 'jq' and uses 'grep' and 'sed' for parsing.
#
# Prerequisites:
#   - curl: command-line tool for transferring data with URLs.
#   - grep, sed: Standard command-line text processing tools.
#
# Usage:
#   1. Fill in the variables in the "CONFIGURABLE VARIABLES" section below.
#   2. Make the script executable: `chmod +x your_script_name.sh`
#   3. Run the script: `./your_script_name.sh`
# ==============================================================================

# --- CONFIGURABLE VARIABLES ---

# Your 3scale admin portal URL (e.g., "my-company-admin.3scale.net")
THREESCALE_ADMIN_URL="<YOUR_3SCALE_ADMIN_PORTAL_URL>"

# Your 3scale access token with "Account Management API" scope and R/W permissions
ACCESS_TOKEN="<YOUR_ACCESS_TOKEN>"

# --- Backend Configuration ---
BACKEND_NAME="My Bash Backend (no-jq)"
# System names should be unique, lowercase, and use underscores instead of spaces.
BACKEND_SYSTEM_NAME="my_bash_backend_no_jq"
# The private URL of the API you want 3scale to manage.
BACKEND_PRIVATE_URL="https://api.internal.mycompany.com/v3"
BACKEND_DESCRIPTION="Backend for the new product (created with Bash)."

# --- Product Configuration ---
PRODUCT_NAME="My Bash Product (no-jq)"
# System names should be unique, lowercase, and use underscores instead of spaces.
PRODUCT_SYSTEM_NAME="my_bash_product_no_jq"
PRODUCT_DESCRIPTION="A new product created and configured via a Bash script."

# The path to mount the backend on the product. Use "/" for the root.
BACKEND_PATH="/"


# --- SCRIPT LOGIC (No need to edit below this line) ---

# Function to check for placeholder values
check_placeholders() {
    if [[ "$THREESCALE_ADMIN_URL" == "<YOUR_3SCALE_ADMIN_PORTAL_URL>" ]] || \
       [[ "$ACCESS_TOKEN" == "<YOUR_ACCESS_TOKEN>" ]]; then
        echo "Error: Please fill in the THREESCALE_ADMIN_URL and ACCESS_TOKEN variables in the script." >&2
        exit 1
    fi
}

check_placeholders

echo "--- 1. Creating a new Backend: '$BACKEND_NAME' ---"

# Create the backend and capture the full response
BACKEND_RESPONSE=$(curl -s -X POST "https://${THREESCALE_ADMIN_URL}/admin/api/backend_apis.json" \
  -d "access_token=${ACCESS_TOKEN}" \
  -d "name=${BACKEND_NAME}" \
  -d "system_name=${BACKEND_SYSTEM_NAME}" \
  -d "private_endpoint=${BACKEND_PRIVATE_URL}" \
  -d "description=${BACKEND_DESCRIPTION}")

# Extract its ID from the JSON response using grep and sed
BACKEND_ID=$(echo "$BACKEND_RESPONSE" | grep -o '"id":[0-9]*' | head -n 1 | sed 's/[^0-9]*//g')

if [[ -z "$BACKEND_ID" ]]; then
    echo "Error: Failed to create the backend. Please check your credentials and configuration." >&2
    echo "API Response:" >&2
    echo "$BACKEND_RESPONSE" >&2
    exit 1
fi

echo "Success! Backend created with ID: $BACKEND_ID"
echo ""


echo "--- 2. Creating a new Product: '$PRODUCT_NAME' ---"

# Create the product and capture the full response
# In the 3scale API, products are referred to as "services".
PRODUCT_RESPONSE=$(curl -s -X POST "https://${THREESCALE_ADMIN_URL}/admin/api/services.json" \
  -d "access_token=${ACCESS_TOKEN}" \
  -d "name=${PRODUCT_NAME}" \
  -d "system_name=${PRODUCT_SYSTEM_NAME}" \
  -d "description=${PRODUCT_DESCRIPTION}")

# Extract its ID from the JSON response
PRODUCT_ID=$(echo "$PRODUCT_RESPONSE" | grep -o '"id":[0-9]*' | head -n 1 | sed 's/[^0-9]*//g')

if [[ -z "$PRODUCT_ID" ]]; then
    echo "Error: Failed to create the product." >&2
    echo "API Response:" >&2
    echo "$PRODUCT_RESPONSE" >&2
    exit 1
fi

echo "Success! Product created with ID: $PRODUCT_ID"
echo ""


echo "--- 3. Associating Backend (ID: $BACKEND_ID) with Product (ID: $PRODUCT_ID) ---"

# Create the backend usage to link the two resources
# -w "\n%{http_code}" appends the HTTP status code to the output
ASSOCIATION_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "https://${THREESCALE_ADMIN_URL}/admin/api/services/${PRODUCT_ID}/backend_usages.json" \
  -d "access_token=${ACCESS_TOKEN}" \
  -d "backend_api_id=${BACKEND_ID}" \
  -d "path=${BACKEND_PATH}")

# Extract the HTTP status code from the last line of the response
HTTP_CODE=$(echo "$ASSOCIATION_RESPONSE" | tail -n1)
JSON_BODY=$(echo "$ASSOCIATION_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -eq 201 ]]; then
    echo "Success! Backend has been associated with the product."
    echo "Response:"
    echo "$JSON_BODY"
else
    echo "Error: Failed to associate backend with product. HTTP Status: $HTTP_CODE" >&2
    echo "Response:" >&2
    echo "$JSON_BODY" >&2
    exit 1
fi

echo ""
echo "--- Automation Complete ---"
