# app.py

import gradio as gr

# Import the logic functions from our modules
from modules.ui_logic import process_property_detail_tab, process_zip_analysis_tab

# --- The README content for our new "Home" tab ---
# This multi-line string holds all the Markdown for the home page.
# The image URLs point to the 'images' folder in your repository.
home_page_content = """
# 🏠 Property Data Explorer & AI Demographic Analyzer 🤖

An interactive web application that transforms raw property data into actionable insights. This tool harnesses the power of the **ATTOM Data API** for real-time property records and leverages a **Google FLAN-T5 Large Language Model** from the Hugging Face Hub to perform demographic analysis.

---

### Application in Action


| Detailed Property Lookup |
| :---: |
| ![Property Detail View](images/image1.png) | 
| Real-time Analysis | 
| ![Property Detail View](images/image2.png) | 
| Demographic Visualization |
| ![Property Detail View](images/image3.png) | 
---

## ✨ Key Features

This application offers two primary features, accessible through the tabs at the top:

### 1. Detailed Property Lookup
Instantly retrieve a comprehensive profile for any property in the United States. Simply enter a full address in the **"Property Detail Lookup"** tab to get a report including:
- **Ownership & Location:** Current owner names, Parcel ID (APN), and subdivision details.
- **Valuation & Tax:** The latest market value, assessed value, and annual tax information.
- **Sale History:** The most recent sale price and date.
- **Building Characteristics:** Property type, year built, living area, and bed/bath count.

### 2. AI-Powered Demographic Analysis
Uncover demographic trends within any ZIP code using the **"ZIP Code Demographic Analysis"** tab. This feature performs a complex, real-time analysis:
1.  Fetches a sample of 100 Single Family Residences from the ATTOM API.
2.  Retrieves the owner's full name for each property.
3.  Uses a **Google FLAN-T5 Large Language Model** to predict the likely national origin of each owner's name.
4.  Generates a dynamic, interactive pie chart visualizing the predicted demographic distribution.

### ⚡️ Advanced Capabilities
- **Efficient Caching:** Implements a persistent, encrypted, file-based cache for both API calls and AI predictions. Subsequent requests for the same data are nearly instantaneous.
- **Real-time Feedback:** A dynamic progress bar and status messages keep the user informed during complex, multi-step analyses.
- **Secure by Design:** All sensitive credentials are managed securely using Hugging Face Repository Secrets. Data at rest in the cache is encrypted.

---

## 🛠️ Technology Stack
- **Frontend UI:** Gradio
- **Backend Logic:** Python
- **Data Source:** ATTOM Data Solutions API
- **AI / Machine Learning:** Hugging Face `transformers` running `google/flan-t5-base`.
- **Data Handling:** Pandas & Plotly Express
- **Security:** `cryptography`
"""


# --- BUILD THE GRADIO INTERFACE with the new Home Tab ---
with gr.Blocks(theme=gr.themes.Soft(), title="Property Explorer") as iface:
    gr.Markdown("# Property Data Explorer")
    gr.Markdown("Powered by the **ATTOM Data API** and **Hugging Face AI**.")

    with gr.Tabs():
        # --- TAB 1: NEW HOME / ABOUT PAGE ---
        with gr.TabItem("About this App"):
            gr.Markdown(home_page_content)

        # --- TAB 2: PROPERTY DETAIL LOOKUP ---
        with gr.TabItem("Property Detail Lookup"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Enter Full Address")
                    street_input1 = gr.Textbox(label="Street Address", placeholder="e.g., 4529 Winona Court")
                    city_input1 = gr.Textbox(label="City", placeholder="e.g., Denver")
                    state_input1 = gr.Textbox(label="State", placeholder="e.g., CO")
                    zip_input1 = gr.Textbox(label="ZIP Code", placeholder="e.g., 80212")
                    btn1 = gr.Button("Get Property Info", variant="primary")
                with gr.Column(scale=2):
                    gr.Markdown("### Property Details")
                    with gr.Tabs():
                        with gr.TabItem("Summary"):
                            summary_output1 = gr.Markdown()
                        with gr.TabItem("Full JSON Response"):
                            json_output1 = gr.JSON()

        # --- TAB 3: ZIP CODE DEMOGRAPHIC ANALYSIS ---
        with gr.TabItem("ZIP Code Demographic Analysis"):
            gr.Markdown("## Analyze Demographics by ZIP Code")
            gr.Markdown("Enter a ZIP code. The app will fetch a sample of 100 Single Family Residences, find the owners, and use AI to analyze their likely national origin.")
            gr.Markdown("**⚠️ Ethical Disclaimer:** Predicting nationality from a name is an imprecise task. This AI model makes a probabilistic guess and can be wrong. It is for illustrative, analytical purposes only.", elem_classes="disclaimer")
            zip_input2 = gr.Textbox(label="Enter a ZIP Code", placeholder="e.g., 80212")
            btn2 = gr.Button("Analyze ZIP Code", variant="primary")
            summary_output2 = gr.Textbox(label="Analysis Status", interactive=False)
            plot_output2 = gr.Plot()
            # --- CHANGE: The DataFrame component has been completely removed ---
            # dataframe_output2 = gr.DataFrame(...) # This line is now deleted

    # --- WIRE UP THE UI COMPONENTS TO THE LOGIC FUNCTIONS ---
    btn1.click(
        fn=process_property_detail_tab,
        inputs=[street_input1, city_input1, state_input1, zip_input1],
        outputs=[summary_output1, json_output1]
    )

    # --- CHANGE: The outputs list for btn2 no longer includes the DataFrame component ---
    btn2.click(
        fn=process_zip_analysis_tab,
        inputs=zip_input2,
        outputs=[summary_output2, plot_output2]
    )

# --- LAUNCH THE APP ---
iface.launch()