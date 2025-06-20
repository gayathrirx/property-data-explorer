# modules/ai_analyzer.py

from transformers import pipeline

# --- Load a SINGLE, reliable, and powerful specialized AI Model ---
# This model ('charles99/name-nationality-classifier') is highly popular and public.
# It uses a BERT-based architecture, which should provide high accuracy.
print("Loading the BERT-based name-nationality classification AI model...")
try:
    _nationality_classifier = pipeline("text-classification", model="charles99/name-nationality-classifier")
    print("AI model loaded successfully.")
except Exception as e:
    # This provides a clearer error if the model fails to load for any reason
    print(f"CRITICAL ERROR: Failed to load the AI model. Exception: {e}")
    # We can create a dummy function so the app doesn't crash completely, but shows an error.
    def _nationality_classifier(names):
        raise RuntimeError("AI Model could not be loaded. Please check the logs.")


def predict_ethnicity(names):
    """
    Takes a list of names and returns a list of predicted nationalities
    using the single, reliable classifier.
    """
    if not names:
        return []
        
    try:
        # The model expects a list of names and returns a list of dictionaries.
        predictions = _nationality_classifier(names)
        # We extract just the 'label' (the nationality string) from each prediction.
        return [pred['label'] for pred in predictions]
    except Exception as e:
        print(f"Error during AI prediction: {e}")
        # Return a list of "Error" strings of the same length as the input
        return ["Error"] * len(names)