# app.py

import gradio as gr

# Import the logic functions from our modules
from modules.ui_logic import process_property_detail_tab, process_zip_analysis_tab

# --- BUILD THE GRADIO INTERFACE ---
with gr.Blocks(theme=gr.themes.Soft(), title="Property Explorer") as iface:
    gr.Markdown("# 🏠 Property Data Explorer")
    gr.Markdown("Powered by the **ATTOM Data API** and **Hugging Face AI**.")

    with gr.Tabs():
        # --- TAB 1: PROPERTY DETAIL LOOKUP (Unchanged) ---
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

        # --- TAB 2: ZIP CODE DEMOGRAPHIC ANALYSIS (UI is Simplified) ---
        with gr.TabItem("ZIP Code Demographic Analysis"):
            gr.Markdown("## Analyze Demographics by ZIP Code")
            gr.Markdown("Enter a ZIP code. The app will fetch a sample of 100 Single Family Residences, find the owners, and use AI to analyze their likely national origin.")
            gr.Markdown("**⚠️ Ethical Disclaimer:** Predicting nationality from a name is an imprecise task. This AI model makes a probabilistic guess and can be wrong. It is for illustrative, analytical purposes only.", elem_classes="disclaimer")
            
            # --- UI CHANGE: Only a single input for the ZIP code ---
            zip_input2 = gr.Textbox(label="Enter a ZIP Code", placeholder="e.g., 82009")
            btn2 = gr.Button("Analyze ZIP Code", variant="primary")
            
            summary_output2 = gr.Textbox(label="Analysis Status", interactive=False)
            plot_output2 = gr.Plot()
            dataframe_output2 = gr.DataFrame(label="Sampled Data and Predictions (Name & Predicted Nationality Only)")

    # --- WIRE UP THE UI COMPONENTS TO THE LOGIC FUNCTIONS ---
    btn1.click(
        fn=process_property_detail_tab,
        inputs=[street_input1, city_input1, state_input1, zip_input1],
        outputs=[summary_output1, json_output1]
    )

    # --- UI CHANGE: The click event now only uses the zip input ---
    btn2.click(
        fn=process_zip_analysis_tab,
        inputs=zip_input2,
        outputs=[summary_output2, plot_output2, dataframe_output2]
    )

# --- LAUNCH THE APP ---
iface.launch()