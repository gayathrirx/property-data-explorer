# modules/attom_api.py

import os
import requests
import gradio as gr

API_KEY = os.environ.get("ATTOM_API_KEY")

def get_property_detail(street_address, city, state):
    """Calls the 'basicprofile' endpoint for a single address."""
    if not API_KEY: raise gr.Error("API Key is not configured.")
    base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
    headers = {"apikey": API_KEY, "Accept": "application/json"}
    params = {'address1': street_address, 'address2': f"{city}, {state}"}
    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def get_addresses_by_zip(zip_code):
    """
    Calls the 'address' endpoint to get a list of addresses in a ZIP code.
    Now includes a filter for Single Family Residences (SFR).
    """
    if not API_KEY: raise gr.Error("API Key is not configured.")
    base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/address"
    headers = {"apikey": API_KEY, "Accept": "application/json"}
    
    # --- CHANGE: Added propertytype filter and kept pagesize at 100 ---
    params = {
        'postalcode': zip_code,
        'propertytype': 'SFR', # Filter for Single Family Residences
        'pagesize': 100
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise gr.Error(f"API Error for ZIP code lookup: {err.response.status_code}. {err.response.text}")
    except requests.exceptions.RequestException as err:
        raise gr.Error(f"A network error occurred: {err}")