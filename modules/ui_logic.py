# modules/ui_logic.py

import pandas as pd
import plotly.express as px
import gradio as gr

# Import our custom helper modules
from .attom_api import get_property_detail, get_addresses_by_zip
from .ai_analyzer import predict_ethnicity

# --- LOGIC FOR THE FIRST UI TAB ---
def process_property_detail_tab(street, city, state, zip_code):
    if not all([street, city, state]): raise gr.Error("Street, City, and State are required.")
    
    data = get_property_detail(street, city, state)
    
    if not data or 'property' not in data or len(data['property']) == 0:
        return "No property found.", {}
        
    prop = data['property'][0]
    address_info = prop.get('address', {}); assessment_info = prop.get('assessment', {}); building_info = prop.get('building', {}); summary_info = prop.get('summary', {}); sale_info = prop.get('sale', {})
    owner1 = assessment_info.get('owner', {}).get('owner1', {}).get('fullName'); owner2 = assessment_info.get('owner', {}).get('owner3', {}).get('fullName')
    all_owners = [o for o in [owner1, owner2] if o and o.strip()]; owner_str = " & ".join(all_owners) if all_owners else "N/A"
    market_value = assessment_info.get('market', {}).get('mktTtlValue'); assessed_value = assessment_info.get('assessed', {}).get('assdTtlValue'); tax_amount = assessment_info.get('tax', {}).get('taxAmt')
    year_built = summary_info.get('yearBuilt'); living_sq_ft = building_info.get('size', {}).get('livingSize'); beds = building_info.get('rooms', {}).get('beds'); baths = building_info.get('rooms', {}).get('bathsTotal')
    sale_price = sale_info.get('saleAmountData', {}).get('saleAmt'); sale_date = sale_info.get('saleAmountData', {}).get('saleRecDate')
    summary = f"""### Property Details for {address_info.get('oneLine', 'N/A')}\n---\n#### **Ownership & Location**\n**Owner(s):** {owner_str}\n**Parcel ID (APN):** {prop.get('identifier', {}).get('apn', 'N/A')}\n**Subdivision:** {prop.get('area', {}).get('subdName', 'N/A')}\n\n#### **Valuation & Tax**\n**Market Value:** {f'${market_value:,}' if market_value else 'N/A'}\n**Assessed Value:** {f'${assessed_value:,}' if assessed_value else 'N/A'}\n**Last Annual Tax:** {f'${tax_amount:,}' if tax_amount else 'N/A'} (Tax Year: {assessment_info.get('tax', {}).get('taxYear', 'N/A')})\n\n#### **Last Sale Information**\n**Sale Price:** {f'${sale_price:,}' if sale_price else 'N/A'}\n**Sale Date:** {sale_date if sale_date else 'N/A'}\n\n#### **Building Characteristics**\n**Property Type:** {summary_info.get('propClass', 'N/A')}\n**Year Built:** {year_built if year_built else 'N/A'}\n**Living Area:** {f'{living_sq_ft:,} sq ft' if living_sq_ft else 'N/A'}\n**Beds / Baths:** {f'{beds} Bed' if beds else 'N/A'} / {f'{baths} Bath' if baths else 'N/A'}"""

    return summary, data

# --- LOGIC FOR THE SECOND UI TAB ---
def process_zip_analysis_tab(zip_code, progress=gr.Progress()):
    if not zip_code: raise gr.Error("A ZIP code is required.")
    
    progress(0, desc="Fetching address list...")
    address_list_data = get_addresses_by_zip(zip_code)
    if not address_list_data or 'property' not in address_list_data:
        return "Could not retrieve addresses for this ZIP code.", None, None

    properties = address_list_data['property']
    total_properties = len(properties)
    owner_data = []

    for i, prop in enumerate(properties):
        progress((i + 1) / total_properties, desc=f"Analyzing address {i+1}/{total_properties}...")
        addr = prop.get('address', {})
        detail_data = get_property_detail(addr.get('line1'), addr.get('locality'), addr.get('countrySubd'))
        if detail_data and 'property' in detail_data and detail_data['property']:
            owner_name = detail_data['property'][0].get('assessment', {}).get('owner', {}).get('owner1', {}).get('fullName')
            if owner_name:
                owner_data.append({'address': addr.get('oneLine'), 'owner_name': owner_name})

    if not owner_data:
        return "No owners found for the sampled addresses.", None, None

    df = pd.DataFrame(owner_data)
    names_to_predict = df['owner_name'].tolist()
    
    progress(1, desc="Running AI analysis on names...")
    ethnicities = predict_ethnicity(names_to_predict)
    df['predicted_ethnicity'] = ethnicities

    ethnicity_counts = df['predicted_ethnicity'].value_counts().reset_index()
    ethnicity_counts.columns = ['Ethnicity', 'Count']

    fig = px.pie(ethnicity_counts, names='Ethnicity', values='Count', 
                 title=f'Predicted Ethnicity Distribution for ZIP Code {zip_code} (Sample of {len(df)} properties)',
                 hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')

    summary = f"Analysis complete. Found {len(df)} property owners to analyze in the sample."
    return summary, fig, df