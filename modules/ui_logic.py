# modules/ui_logic.py

import pandas as pd
import plotly.express as px
import gradio as gr

from .attom_api import get_property_detail, get_addresses_by_zip
from .ai_analyzer import predict_ethnicity

# --- LOGIC FOR THE FIRST UI TAB (Unchanged) ---
def process_property_detail_tab(street, city, state, zip_code):
    if not all([street, city, state]): raise gr.Error("Street, City, and State are required.")
    data = get_property_detail(street, city, state)
    if not data or 'property' not in data or len(data['property']) == 0:
        return "No property found.", {}
    prop = data['property'][0]
    address_info=prop.get('address',{});assessment_info=prop.get('assessment',{});building_info=prop.get('building',{});summary_info=prop.get('summary',{});sale_info=prop.get('sale',{})
    owner1=assessment_info.get('owner',{}).get('owner1',{}).get('fullName');owner2=assessment_info.get('owner',{}).get('owner3',{}).get('fullName')
    all_owners=[o for o in [owner1,owner2] if o and o.strip()];owner_str=" & ".join(all_owners) if all_owners else "N/A"
    market_value=assessment_info.get('market',{}).get('mktTtlValue');assessed_value=assessment_info.get('assessed',{}).get('assdTtlValue');tax_amount=assessment_info.get('tax',{}).get('taxAmt')
    year_built=summary_info.get('yearBuilt');living_sq_ft=building_info.get('size',{}).get('livingSize');beds=building_info.get('rooms',{}).get('beds');baths=building_info.get('rooms',{}).get('bathsTotal')
    sale_price=sale_info.get('saleAmountData',{}).get('saleAmt');sale_date=sale_info.get('saleAmountData',{}).get('saleRecDate')
    summary = f"""### Property Details for {address_info.get('oneLine', 'N/A')}\n---\n#### **Ownership & Location**\n**Owner(s):** {owner_str}\n**Parcel ID (APN):** {prop.get('identifier', {}).get('apn', 'N/A')}\n**Subdivision:** {prop.get('area', {}).get('subdName', 'N/A')}\n\n#### **Valuation & Tax**\n**Market Value:** {f'${market_value:,}' if market_value else 'N/A'}\n**Assessed Value:** {f'${assessed_value:,}' if assessed_value else 'N/A'}\n**Last Annual Tax:** {f'${tax_amount:,}' if tax_amount else 'N/A'} (Tax Year: {assessment_info.get('tax', {}).get('taxYear', 'N/A')})\n\n#### **Last Sale Information**\n**Sale Price:** {f'${sale_price:,}' if sale_price else 'N/A'}\n**Sale Date:** {sale_date if sale_date else 'N/A'}\n\n#### **Building Characteristics**\n**Property Type:** {summary_info.get('propClass', 'N/A')}\n**Year Built:** {year_built if year_built else 'N/A'}\n**Living Area:** {f'{living_sq_ft:,} sq ft' if living_sq_ft else 'N/A'}\n**Beds / Baths:** {f'{beds} Bed' if beds else 'N/A'} / {f'{baths} Bath' if baths else 'N/A'}"""
    return summary, data

# --- LOGIC FOR THE SECOND UI TAB (Simplified for ZIP-only analysis) ---
def process_zip_analysis_tab(zip_code, progress=gr.Progress()):
    if not zip_code:
        raise gr.Error("A ZIP code is required.")

    # --- Step 1: Bulk fetch SFR addresses from the ZIP code ---
    progress(0, desc="Fetching property list (sample of 100 SFRs)...")
    address_list_data = get_addresses_by_zip(zip_code)
    if not address_list_data or 'property' not in address_list_data:
        return "Could not retrieve addresses for this ZIP code.", None, None

    # --- Step 2: Loop through the list to get owner names ---
    properties = address_list_data['property']
    total_to_process = len(properties)
    owner_names = []
    
    if total_to_process == 0:
        return f"No Single Family Residences found in the first 100 properties for ZIP {zip_code}.", None, None

    for i, prop in enumerate(properties):
        progress((i / total_to_process) * 0.9, desc=f"Getting owner for property {i+1}/{total_to_process}...")
        addr = prop.get('address', {})
        # Making a detail call for each property in the list
        detail_data = get_property_detail(addr.get('line1'), addr.get('locality'), addr.get('countrySubd'))
        if detail_data and 'property' in detail_data and detail_data['property']:
            owner_name = detail_data['property'][0].get('assessment', {}).get('owner', {}).get('owner1', {}).get('fullName')
            if owner_name:
                owner_names.append(owner_name)
    
    if not owner_names:
        return "Found properties, but could not retrieve any owner names.", None, None

    # --- Step 3: Run AI analysis ---
    progress(0.9, desc="Running AI analysis on names...")
    ethnicities = predict_ethnicity(owner_names)
    
    df = pd.DataFrame({"Owner Name": owner_names, "Predicted Nationality": ethnicities})

    # --- Step 4: Create chart and return results ---
    progress(1, desc="Creating chart...")
    ethnicity_counts = df['Predicted Nationality'].value_counts().reset_index()
    ethnicity_counts.columns = ['Nationality', 'Count']
    
    fig = px.pie(ethnicity_counts, names='Nationality', values='Count', 
                 title=f'Predicted Nationality Distribution for ZIP {zip_code} (Sample of {len(df)} SFRs)',
                 hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')

    summary = f"Analysis complete. Found and analyzed {len(df)} property owners from the sample."
    return summary, fig, df