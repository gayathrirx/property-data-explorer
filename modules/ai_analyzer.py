# modules/ai_analyzer.py

from transformers import pipeline

# Load the model once when the module is first imported. This is very efficient.
print("Loading ethnicity classification AI model...")
_ethnicity_classifier = pipeline("text-classification", model="johngiorgi/name-ethnicity-classification-v1")
print("AI model loaded.")

def predict_ethnicity(names):
    """Takes a list of names and returns a list of predicted ethnicities."""
    if not names:
        return []
    # The model expects a list of names and returns a list of dictionaries.
    predictions = _ethnicity_classifier(names)
    # We extract just the 'label' (the ethnicity string) from each prediction.
    return [pred['label'] for pred in predictions]