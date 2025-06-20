# modules/ai_analyzer.py

from transformers import pipeline

print("Loading multiple AI models for ensemble analysis...")

# --- Load all three models ---
# Each is stored in a dictionary for easy access.
_classifiers = {
    "baseline": pipeline("text-classification", model="matthew-so/name-nationality-classification"),
    "bert": pipeline("text-classification", model="charles99/name-nationality-classifier"),
    "llm": pipeline("text2text-generation", model="google/flan-t5-base")
}
print("All AI models loaded.")

# A fixed list of categories for the LLM to ensure consistent output
LLM_CATEGORIES = ['English', 'Russian', 'Arabic', 'Chinese', 'Italian', 'Spanish', 'Japanese', 'French', 'German', 'Dutch', 'Greek', 'Indian', 'Korean', 'Portuguese', 'Vietnamese', 'Polish', 'Czech', 'Irish']

def get_ensemble_predictions(names):
    """
    Gets predictions from all three models for a list of names.
    Returns a list of dictionaries, where each dict has the predictions from all models for one name.
    """
    if not names:
        return []

    # Get predictions from the fast classifiers first
    baseline_preds = [p['label'] for p in _classifiers["baseline"](names)]
    bert_preds = [p['label'] for p in _classifiers["bert"](names)]
    
    # Get predictions from the slower LLM one by one
    llm_preds = []
    for name in names:
        prompt = f"Predict the linguistic origin of the name '{name}' from this list: {', '.join(LLM_CATEGORIES)}. Respond with only one word from the list."
        response = _classifiers["llm"](prompt, max_length=10)[0]['generated_text'].strip()
        llm_preds.append(response if response in LLM_CATEGORIES else "Unknown")
        
    # Combine the results
    combined_results = []
    for i in range(len(names)):
        combined_results.append({
            "name": names[i],
            "baseline_pred": baseline_preds[i],
            "bert_pred": bert_preds[i],
            "llm_pred": llm_preds[i]
        })
        
    return combined_results