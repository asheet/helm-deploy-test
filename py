#!/usr/bin/env python3

# ==============================================================================
# 3scale Backend and Product Creation Script (Python)
#
# This script automates the creation of a new backend, a new product,
# and associates the backend with the product in Red Hat 3scale using the
# 3scale Admin REST API.
#
# Prerequisites:
#   - Python 3
#   - The 'requests' library.
#       Install it using pip: `pip install requests`
#
# Usage:
#   1. Fill in the variables in the "CONFIGURABLE VARIABLES" section below.
#   2. Run the script from your terminal: `python your_script_name.py`
# ==============================================================================

import requests
import sys
import json

# --- CONFIGURABLE VARIABLES ---

# Your 3scale admin portal URL (e.g., "my-company-admin.3scale.net")
THREESCALE_ADMIN_URL = "<YOUR_3SCALE_ADMIN_PORTAL_URL>"

# Your 3scale access token with "Account Management API" scope and R/W permissions
ACCESS_TOKEN = "<YOUR_ACCESS_TOKEN>"

# --- Backend Configuration ---
BACKEND_NAME = "My Automated Python Backend"
# System names should be unique, lowercase, and use underscores instead of spaces.
BACKEND_SYSTEM_NAME = "my_automated_python_backend"
# The private URL of the API you want 3scale to manage.
BACKEND_PRIVATE_URL = "https://api.internal.mycompany.com/v2"
BACKEND_DESCRIPTION = "Backend for the new automated product (created with Python)."

# --- Product Configuration ---
PRODUCT_NAME = "My Automated Python Product"
# System names should be unique, lowercase, and use underscores instead of spaces.
PRODUCT_SYSTEM_NAME = "my_automated_python_product"
PRODUCT_DESCRIPTION = "A new product created and configured via a Python script."

# The path to mount the backend on the product. Use "/" for the root.
BACKEND_PATH = "/"


# --- SCRIPT LOGIC (No need to edit below this line) ---

def check_placeholders():
    """Checks if the user has replaced the placeholder credentials."""
    if (THREESCALE_ADMIN_URL == "<YOUR_3SCALE_ADMIN_PORTAL_URL>" or
            ACCESS_TOKEN == "<YOUR_ACCESS_TOKEN>"):
        print("Error: Please fill in the THREESCALE_ADMIN_URL and ACCESS_TOKEN variables in the script.", file=sys.stderr)
        sys.exit(1)

def create_backend():
    """Creates a new backend in 3scale and returns its ID."""
    print(f"--- 1. Creating a new Backend: '{BACKEND_NAME}' ---")
    url = f"https://{THREESCALE_ADMIN_URL}/admin/api/backend_apis.json"
    
    payload = {
        'access_token': ACCESS_TOKEN,
        'name': BACKEND_NAME,
        'system_name': BACKEND_SYSTEM_NAME,
        'private_endpoint': BACKEND_PRIVATE_URL,
        'description': BACKEND_DESCRIPTION
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        
        backend_data = response.json()
        backend_id = backend_data.get('backend_api', {}).get('id')
        
        if not backend_id:
            print("Error: Could not parse backend ID from API response.", file=sys.stderr)
            print("Response:", json.dumps(backend_data, indent=2), file=sys.stderr)
            return None
            
        print(f"Success! Backend created with ID: {backend_id}\n")
        return backend_id
        
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to create the backend. Please check your credentials and configuration.", file=sys.stderr)
        print(f"Exception: {e}", file=sys.stderr)
        return None

def create_product():
    """Creates a new product in 3scale and returns its ID."""
    print(f"--- 2. Creating a new Product: '{PRODUCT_NAME}' ---")
    # In the 3scale API, products are referred to as "services".
    url = f"https://{THREESCALE_ADMIN_URL}/admin/api/services.json"
    
    payload = {
        'access_token': ACCESS_TOKEN,
        'name': PRODUCT_NAME,
        'system_name': PRODUCT_SYSTEM_NAME,
        'description': PRODUCT_DESCRIPTION
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        product_data = response.json()
        product_id = product_data.get('service', {}).get('id')
        
        if not product_id:
            print("Error: Could not parse product ID from API response.", file=sys.stderr)
            print("Response:", json.dumps(product_data, indent=2), file=sys.stderr)
            return None

        print(f"Success! Product created with ID: {product_id}\n")
        return product_id

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to create the product.", file=sys.stderr)
        print(f"Exception: {e}", file=sys.stderr)
        return None

def associate_backend_to_product(product_id, backend_id):
    """Associates an existing backend with a product."""
    print(f"--- 3. Associating Backend (ID: {backend_id}) with Product (ID: {product_id}) ---")
    url = f"https://{THREESCALE_ADMIN_URL}/admin/api/services/{product_id}/backend_usages.json"
    
    payload = {
        'access_token': ACCESS_TOKEN,
        'backend_api_id': backend_id,
        'path': BACKEND_PATH
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()

        print("Success! Backend has been associated with the product.")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to associate backend with product.", file=sys.stderr)
        print(f"Exception: {e}", file=sys.stderr)
        # Attempt to print error from 3scale if available
        try:
            print("Error details from API:", json.dumps(response.json(), indent=2), file=sys.stderr)
        except json.JSONDecodeError:
            print("Could not decode JSON from error response.", file=sys.stderr)
        return False

def main():
    """Main function to orchestrate the API creation process."""
    check_placeholders()
    
    backend_id = create_backend()
    if not backend_id:
        sys.exit(1)
        
    product_id = create_product()
    if not product_id:
        # Optional: Add cleanup logic here to delete the created backend if product creation fails.
        sys.exit(1)
        
    if associate_backend_to_product(product_id, backend_id):
        print("\n--- Automation Complete ---")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
