import gradio as gr
import requests
import json
import os

# --- 1. Get the API key securely (No changes needed) ---
API_KEY = os.environ.get("ATTOM_API_KEY")

# --- 2. The Core API Function (This is now confirmed to be correct) ---
def get_property_info_from_attom(street_address, city, state, zip_code):
    """
    Fetches property information from the ATTOM Data API using the correct gateway URL and parameters.
    """
    if not API_KEY:
        raise gr.Error("API Key not configured. Please set the ATTOM_API_KEY secret in your Space settings.")

    base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
    headers = {"apikey": API_KEY, "Accept": "application/json"}
    
    # This endpoint works best with 'address1' and 'address2'
    params = {'address1': street_address, 'address2': f"{city}, {state}"}

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        raise gr.Error(f"API Error: {err.response.status_code}. Details: {error_details}")
    except requests.exceptions.RequestException as err:
        raise gr.Error(f"A network error occurred: {err}")

# --- 3. The Gradio Display Function (Completely Rewritten to Parse the Full JSON) ---
def process_and_display_property_info(street, city, state, zip_code):
    """
    Calls the ATTOM API and formats the rich JSON structure into a comprehensive summary.
    """
    if not all([street, city, state]): # Zip code is helpful but not always required by the API
        raise gr.Error("Street Address, City, and State are required.")
    
    data = get_property_info_from_attom(street, city, state, zip_code)
    
    if not data or 'property' not in data or len(data['property']) == 0:
        return "No property found for the given address.", {}

    prop = data['property'][0]
    
    # --- Navigate the rich JSON structure to extract detailed information ---
    address_info = prop.get('address', {})
    assessment_info = prop.get('assessment', {})
    building_info = prop.get('building', {})
    summary_info = prop.get('summary', {})
    sale_info = prop.get('sale', {})

    # Safely get owner names (handles multiple owners)
    owner1 = assessment_info.get('owner', {}).get('owner1', {}).get('fullName')
    owner2 = assessment_info.get('owner', {}).get('owner3', {}).get('fullName') # Note: JSON shows owner3, not owner2
    all_owners = [o for o in [owner1, owner2] if o and o.strip()]
    owner_str = " & ".join(all_owners) if all_owners else "N/A"

    # Get valuation data
    assessed_value = assessment_info.get('assessed', {}).get('assdTtlValue')
    market_value = assessment_info.get('market', {}).get('mktTtlValue')
    tax_amount = assessment_info.get('tax', {}).get('taxAmt')

    # Get building/summary data
    year_built = summary_info.get('yearBuilt')
    living_sq_ft = building_info.get('size', {}).get('livingSize')
    beds = building_info.get('rooms', {}).get('beds')
    baths = building_info.get('rooms', {}).get('bathsTotal')

    # Get last sale data
    sale_price = sale_info.get('saleAmountData', {}).get('saleAmt')
    sale_date = sale_info.get('saleAmountData', {}).get('saleRecDate')

    # --- Format a rich, multi-section summary using Markdown ---
    summary = f"""
    ### Property Details for {address_info.get('oneLine', 'N/A')}
    ---
    #### **Ownership & Location**
    **Owner(s):** {owner_str}
    **Parcel ID (APN):** {prop.get('identifier', {}).get('apn', 'N/A')}
    **Subdivision:** {prop.get('area', {}).get('subdName', 'N/A')}
    
    #### **Valuation & Tax**
    **Market Value:** {f'${market_value:,}' if market_value else 'N/A'}
    **Assessed Value:** {f'${assessed_value:,}' if assessed_value else 'N/A'}
    **Last Annual Tax:** {f'${tax_amount:,}' if tax_amount else 'N/A'} (Tax Year: {assessment_info.get('tax', {}).get('taxYear', 'N/A')})

    #### **Last Sale Information**
    **Sale Price:** {f'${sale_price:,}' if sale_price else 'N/A'}
    **Sale Date:** {sale_date if sale_date else 'N/A'}

    #### **Building Characteristics**
    **Property Type:** {summary_info.get('propClass', 'N/A')}
    **Year Built:** {year_built if year_built else 'N/A'}
    **Living Area:** {f'{living_sq_ft:,} sq ft' if living_sq_ft else 'N/A'}
    **Beds / Baths:** {f'{beds} Bed' if beds else 'N/A'} / {f'{baths} Bath' if baths else 'N/A'}
    """
    
    return summary, data

# --- 4. Build the Generic Gradio Interface ---
with gr.Blocks(theme=gr.themes.Soft(), title="Property Explorer (ATTOM)") as iface:
    gr.Markdown("# 🏠 Property Information Explorer")
    gr.Markdown("Enter a property address to fetch public record data using the **ATTOM Data API**.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Enter Address")
            street_input = gr.Textbox(label="Street Address", placeholder="e.g., 1600 Pennsylvania Ave NW")
            city_input = gr.Textbox(label="City", placeholder="e.g., Washington")
            # State input is no longer defaulted to "TX"
            state_input = gr.Textbox(label="State", placeholder="e.g., DC")
            zip_input = gr.Textbox(label="ZIP Code", placeholder="e.g., 20500")
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

    # Examples are now generic
    gr.Examples(
        examples=[
            ["4529 Winona Court", "Denver", "CO", "80212"],
            ["1600 Pennsylvania Ave NW", "Washington", "DC", "20500"],
            ["221B Baker St", "London", "", ""], # Example that will likely fail gracefully
        ],
        inputs=[street_input, city_input, state_input, zip_input]
    )

# --- 5. Launch the app ---
iface.launch()