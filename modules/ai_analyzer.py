# modules/ai_analyzer.py

from transformers import pipeline

# --- Load a SINGLE, STABLE, Google-hosted Foundational Model ---
# This model is guaranteed to be available and will not be deleted.
# We will control its accuracy through better prompting.
print("Loading Google FLAN-T5 Foundational AI Model...")
try:
    _llm_classifier = pipeline("text2text-generation", model="google/flan-t5-base")
    print("Google AI model loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load the Google FLAN-T5 model. Exception: {e}")
    # Create a dummy function so the app doesn't crash, but shows an error.
    def _llm_classifier(names):
        raise RuntimeError("AI Model could not be loaded. Please check the logs.")

# --- Define a clear, comprehensive list of categories for the LLM ---
# This list is a key part of the prompt that constrains the model's output.
NATIONALITY_CATEGORIES = [
    'Arabic', 'Chinese', 'Czech', 'Dutch', 'English', 'French', 'German', 
    'Greek', 'Indian', 'Irish', 'Italian', 'Japanese', 'Korean', 'Polish', 
    'Portuguese', 'Russian', 'Scottish', 'Spanish', 'Vietnamese'
]

def predict_ethnicity(names):
    """
    Takes a list of names and uses a powerful LLM with a detailed prompt
    to predict the most likely nationality from a fixed list of categories.
    """
    if not names:
        return []

    predictions = []
    for name in names:
        # --- SUPERIOR PROMPT ENGINEERING TO IMPROVE ACCURACY ---
        # We give the model a clear role, context, a specific task, the list
        # of valid outputs, and a strong command to only use a word from that list.
        prompt = f"""
        As an expert linguist specializing in onomastics (the study of names), analyze the following name to determine its most likely geographical and linguistic origin.

        Name: "{name}"

        From the following list of nationalities, which is the most probable origin for this name?
        List: {", ".join(NATIONALITY_CATEGORIES)}

        Respond with only a single word from the list.
        """

        try:
            response = _llm_classifier(prompt, max_length=10)[0]['generated_text'].strip()
            
            # Final safety check: ensure the model's output is one of our categories.
            # If not, we default to "Unknown" to prevent bad data.
            if response in NATIONALITY_CATEGORIES:
                predictions.append(response)
            else:
                # This can happen if the model says e.g. "The origin is English."
                # We can try a simple find.
                found = False
                for cat in NATIONALITY_CATEGORIES:
                    if cat.lower() in response.lower():
                        predictions.append(cat)
                        found = True
                        break
                if not found:
                    predictions.append("Unknown")

        except Exception as e:
            print(f"Error processing name '{name}': {e}")
            predictions.append("Error")
            
    return predictions