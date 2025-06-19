import gradio as gr
import requests
import json
import os

# --- 1. Get the NEW API key securely ---
# We now get the ATTOM_API_KEY from the repository secrets.
API_KEY = os.environ.get("ATTOM_API_KEY")

# --- 2. The Core API Function (Modified for ATTOM) ---
def get_property_info_from_attom(street_address, city, state, zip_code):
    """
    Fetches property information from the ATTOM Data API.
    Returns the full JSON response or None if an error occurs.
    """
    if not API_KEY:
        raise gr.Error("API Key not configured. Please set the ATTOM_API_KEY secret in your Space settings.")

    # --- ATTOM API Specifics ---
    # The base URL and endpoint are different.
    base_url = "https://api.attomdata.com/propertyapi/v1.0.0/property/detail"
    
    # The authentication header is different. It expects a header named 'apikey'.
    headers = {
        "apikey": API_KEY,
        "Accept": "application/json" # It's good practice to specify the expected response format.
    }
    
    # The address parameters are different.
    params = {
        'address1': street_address,
        'address2': f"{city}, {state} {zip_code}"
    }
    # --- End ATTOM Specifics ---

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        raise gr.Error(f"API Error: {err.response.status_code}. Details: {error_details}")
    except requests.exceptions.RequestException as err:
        raise gr.Error(f"A network error occurred: {err}")

# --- 3. The Gradio Display Function (Modified for ATTOM's JSON structure) ---
def process_and_display_property_info(street, city, state, zip_code):
    """
    Calls the ATTOM API and formats the new JSON structure for display.
    """
    if not all([street, city, state, zip_code]):
        raise gr.Error("All address fields are required.")
    
    data = get_property_info_from_attom(street, city, state, zip_code)
    
    if not data or 'property' not in data or len(data['property']) == 0:
        return "No property found for the given address.", {}

    # ATTOM's data is nested inside a 'property' list.
    prop = data['property'][0]
    
    # --- Navigate the NEW JSON structure safely using .get() ---
    address_info = prop.get('address', {})
    assessment_info = prop.get('assessment', {})
    building_info = prop.get('building', {})
    
    owner_info = assessment_info.get('owner', {}).get('owner1', {})
    owner_name = f"{owner_info.get('firstName', '')} {owner_info.get('lastName', '')}".strip()
    
    assessed_value = assessment_info.get('assessed', {}).get('assessedValue', 0)
    tax_amount = assessment_info.get('tax', {}).get('taxAmt', 0)
    
    year_built = building_info.get('summary', {}).get('yearBuilt', 'N/A')
    square_feet = building_info.get('size', {}).get('grossSize', 'N/A')
    
    parcel_id = assessment_info.get('parcel', {}).get('apn', 'N/A')
    
    # --- Format a nice summary using the new data paths ---
    summary = f"""
    ### Property Summary for {address_info.get('oneLine', 'N/A')}
    ---
    **Owner:** {owner_name if owner_name else 'N/A'}
    **Assessed Value:** ${assessed_value:,}
    **Last Annual Tax:** ${tax_amount:,}
    **Year Built:** {year_built}
    **Square Feet:** {square_feet:,} sq ft
    **Parcel ID (APN):** {parcel_id}
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
            ["2001 E 8th St", "Austin", "TX", "78702"],
            ["3500 Grand Ave", "Dallas", "TX", "75210"]
        ],
        inputs=[street_input, city_input, state_input, zip_input]
    )

# --- 5. Launch the app ---
iface.launch()