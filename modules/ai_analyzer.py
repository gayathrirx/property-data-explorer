# modules/ai_analyzer.py

from transformers import pipeline

# --- Load the new AI Model ---
# We now use a general-purpose, instruction-tuned model from Google.
# The pipeline type changes to "text2text-generation".
print("Loading Google FLAN-T5 AI model...")
_llm_classifier = pipeline("text2text-generation", model="google/flan-t5-base")
print("AI model loaded.")

# --- Define our fixed output categories ---
# This is crucial for getting structured data back from the LLM.
ETHNICITY_CATEGORIES = [
    'English', 'Russian', 'Arabic', 'Chinese', 'Italian', 'Spanish', 
    'Japanese', 'French', 'German', 'Dutch', 'Greek', 'Indian', 
    'Korean', 'Portuguese', 'Vietnamese', 'Polish', 'Czech', 'Irish'
]

def predict_ethnicity(names):
    """
    Takes a list of names, prompts the LLM for each one, and returns a list
    of predicted ethnicities from our fixed list of categories.
    """
    if not names:
        return []

    predictions = []
    for name in names:
        # --- Prompt Engineering ---
        # We create a detailed instruction for the LLM for each name.
        prompt = f"""
        You are an expert linguist. Based on the full name, predict the most likely
        linguistic origin or ethnicity from the following list: {", ".join(ETHNICITY_CATEGORIES)}.

        The name is: "{name}"

        Respond with only a single word from the list.
        """

        try:
            # Generate the response from the LLM
            response = _llm_classifier(prompt, max_length=10)
            # The output is like [{'generated_text': 'English'}]. We extract the text.
            generated_text = response[0]['generated_text'].strip()
            
            # To be safe, ensure the model's output is one of our categories.
            # If not, we default to "Unknown".
            if generated_text in ETHNICITY_CATEGORIES:
                predictions.append(generated_text)
            else:
                predictions.append("Unknown")

        except Exception as e:
            print(f"Error processing name '{name}': {e}")
            predictions.append("Error")
            
    return predictions