import gradio as gr
import requests
import json
import os

# --- 1. Get the API key securely (No change here) ---
API_KEY = os.environ.get("ATTOM_API_KEY")

# --- 2. The Core API Function (Updated to match your working curl command) ---
def get_property_info_from_attom(street_address, city, state, zip_code):
    """
    Fetches property information from the ATTOM Data API's 'basicprofile' endpoint
    using the correct gateway URL and parameters.
    """
    if not API_KEY:
        raise gr.Error("API Key not configured. Please set the ATTOM_API_KEY secret in your Space settings.")

    # --- CRITICAL UPDATE 1: Correct URL based on your curl command ---
    # The hostname is 'api.gateway.attomdata.com'.
    base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
    
    headers = {
        "apikey": API_KEY,
        "Accept": "application/json"
    }
    
    # --- CRITICAL UPDATE 2: Correct parameters based on your curl command ---
    # This endpoint expects 'address1' and 'address2'.
    params = {
        'address1': street_address,
        'address2': f"{city}, {state}" # ZIP code is often not needed if city/state are provided
    }
    # --- End of Updates ---

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        # A 401 error here would now indicate an issue with the key value itself, not the URL.
        error_details = err.response.text
        raise gr.Error(f"API Error: {err.response.status_code}. Details: {error_details}")
    except requests.exceptions.RequestException as err:
        raise gr.Error(f"A network error occurred: {err}")

# --- 3. The Gradio Display Function (Modified for the 'basicprofile' JSON structure) ---
def process_and_display_property_info(street, city, state, zip_code):
    """
    Calls the ATTOM 'basicprofile' API and formats the JSON structure for display.
    """
    if not all([street, city, state, zip_code]):
        raise gr.Error("All address fields are required.")
    
    data = get_property_info_from_attom(street, city, state, zip_code)
    
    if not data or 'property' not in data or len(data['property']) == 0:
        return "No property found for the given address.", {}

    prop = data['property'][0]
    
    # --- Navigate the JSON structure from the 'basicprofile' endpoint ---
    address_info = prop.get('address', {})
    location_info = prop.get('location', {})
    lot_info = prop.get('lot', {})
    area_info = prop.get('area', {})
    
    county = location_info.get('county', 'N/A')
    lot_size = lot_info.get('lotsize1', 0)
    building_size = area_info.get('bldgsize', 0)
    parcel_id = prop.get('identifier', {}).get('apn', 'N/A')
    
    summary = f"""
    ### Basic Profile for {address_info.get('oneLine', 'N/A')}
    ---
    **County:** {county}
    **Parcel ID (APN):** {parcel_id}
    **Building Size:** {building_size:,} sq ft
    **Lot Size:** {lot_size:,} (units may vary)

    **Note:** The 'basicprofile' endpoint does not provide owner, tax, or value data.
    """
    
    return summary, data

# --- 4. Build the Gradio Interface (No changes needed here) ---
with gr.Blocks(theme=gr.themes.Soft(), title="Texas Property Explorer (ATTOM)") as iface:
    gr.Markdown("# 🏠 Texas Property Information Explorer")
    gr.Markdown("Enter a Texas property address to fetch public record data using the **ATTOM Data API**.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Enter Address")
            street_input = gr.Textbox(label="Street Address", placeholder="e.g., 1100 Congress Ave")
            city_input = gr.Textbox(label="City", placeholder="e.g., Austin")
            state_input = gr.Textbox(label="State", value="TX")
            zip_input = gr.Textbox(label="ZIP Code", placeholder="e.g., 78701")
            btn = gr.Button("Get Property Info", variant="primary")

        with gr.Column(scale=2):
            gr.Markdown("### Property Details")
            with gr.Tabs():
                with gr.TabItem("Summary"):
                    summary_output = gr.Markdown()
                with gr.TabItem("Full JSON Response"):
                    json_output = gr.JSON()

    btn.click(
        fn=process_and_display_property_info,
        inputs=[street_input, city_input, state_input, zip_input],
        outputs=[summary_output, json_output]
    )

    gr.Examples(
        examples=[
            ["1100 Congress Ave", "Austin", "TX", "78701"],
            ["4529 Winona Court", "Denver", "CO", "80212"], # Your example from curl
            ["3500 Grand Ave", "Dallas", "TX", "75210"]
        ],
        inputs=[street_input, city_input, state_input, zip_input]
    )

# --- 5. Launch the app ---
iface.launch()