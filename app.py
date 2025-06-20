# app.py

import gradio as gr

# Import the main processing functions from our new ui_logic module
from modules.ui_logic import process_property_detail_tab, process_zip_analysis_tab

# --- BUILD THE GRADIO INTERFACE ---
with gr.Blocks(theme=gr.themes.Soft(), title="Property Explorer") as iface:
    gr.Markdown("# 🏠 Property Data Explorer")
    gr.Markdown("Powered by the **ATTOM Data API** and **Hugging Face AI**.")

    with gr.Tabs():
        # --- TAB 1: PROPERTY DETAIL LOOKUP ---
        with gr.TabItem("Property Detail Lookup"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Enter Address")
                    street_input = gr.Textbox(label="Street Address", placeholder="e.g., 1600 Pennsylvania Ave NW")
                    city_input = gr.Textbox(label="City", placeholder="e.g., Washington")
                    state_input = gr.Textbox(label="State", placeholder="e.g., DC")
                    zip_input = gr.Textbox(label="ZIP Code", placeholder="e.g., 20500")
                    btn1 = gr.Button("Get Property Info", variant="primary")
                with gr.Column(scale=2):
                    gr.Markdown("### Property Details")
                    with gr.Tabs():
                        with gr.TabItem("Summary"):
                            summary_output1 = gr.Markdown()
                        with gr.TabItem("Full JSON Response"):
                            json_output1 = gr.JSON()
            
            gr.Examples(
                examples=[["4529 Winona Court", "Denver", "CO", "80212"]],
                inputs=[street_input, city_input, state_input, zip_input]
            )

        # --- TAB 2: ZIP CODE DEMOGRAPHIC ANALYSIS ---
        with gr.TabItem("ZIP Code Demographic Analysis"):
            gr.Markdown("## Analyze Demographics by ZIP Code")
            gr.Markdown("This tool gets a sample of properties from a ZIP code, finds the owner's name for each, and uses AI to predict the likely ethnicity distribution.")
            gr.Markdown("**⚠️ Ethical Disclaimer:** Predicting ethnicity from a name is an imprecise task. This AI model makes a probabilistic guess and can be wrong. It is for illustrative, analytical purposes only and should not be used to make decisions about individuals.", elem_classes="disclaimer")
            
            with gr.Row():
                zip_input2 = gr.Textbox(label="Enter a ZIP Code", placeholder="e.g., 82009")
                btn2 = gr.Button("Analyze ZIP Code", variant="primary")
            
            summary_output2 = gr.Textbox(label="Analysis Status", interactive=False)
            plot_output2 = gr.Plot()
            dataframe_output2 = gr.DataFrame(label="Sampled Data and Predictions")

    # --- WIRE UP THE UI COMPONENTS TO THE LOGIC FUNCTIONS ---
    btn1.click(
        fn=process_property_detail_tab,
        inputs=[street_input, city_input, state_input, zip_input],
        outputs=[summary_output1, json_output1]
    )

    btn2.click(
        fn=process_zip_analysis_tab,
        inputs=zip_input2,
        outputs=[summary_output2, plot_output2, dataframe_output2]
    )

# --- LAUNCH THE APP ---
iface.launch()