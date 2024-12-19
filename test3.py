import spacy
import re

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Define the AG-Rules for identifying relationships
AG_RULES = {
    "composition": [
        "comprise", "have", "include", "possess", "contain", 
        "consist of", "constitute", "embed", "incorporate", 
        "encompass", "entail", "hold", "composed of", 
        "make up", "own"
    ],
    "aggregation": [
        "is a part of", "are a part of", 
        "is associated with", "are associated with",
        "belongs to", "belong to",  # Added here
        "is connected to", "relates to",
        "forms part of", "is included in"
    ]
}

# Combine all phrases into a single list for quick search
ALL_PHRASES = AG_RULES["composition"] + AG_RULES["aggregation"]

# Function to identify relationship type based on AG-Rules
def identify_relationship(sentence):
    # Check for multi-word phrases in the original sentence
    phrase_found = None
    for phrase in ALL_PHRASES:
        # Using regex to find exact phrases
        if re.search(rf"\b{re.escape(phrase)}\b", sentence, re.IGNORECASE):
            phrase_found = phrase
            break

    # Initialize variables
    subject = None
    obj = None
    verb = None
    relationship_type = None

    # Parse the sentence using SpaCy
    doc = nlp(sentence)

    # Extract subject, verb, and object
    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass"):  # Subject (including passive)
            subject = token.text
        elif token.dep_ == "dobj":
            obj = token.text
        elif token.pos_ == "ROOT":
            # Use lemma to match singular/plural forms
            verb = token.lemma_
        elif token.dep_ == "pobj":  # For prepositions
            obj = token.text

    # Determine the relationship based on multi-word phrases or verb
    if phrase_found:
        if phrase_found in AG_RULES["composition"]:
            relationship_type = "Composition"
            relationship = {"class_1": obj, "association_label": phrase_found, "class_2": subject, "type": relationship_type}
        elif phrase_found in AG_RULES["aggregation"]:
            relationship_type = "Weak Aggregation"
            relationship = {"class_1": subject, "association_label": phrase_found, "class_2": obj, "type": relationship_type}
    elif verb in AG_RULES["composition"]:
        relationship_type = "Composition"
        relationship = {"class_1": obj, "association_label": verb, "class_2": subject, "type": relationship_type}
    elif verb in AG_RULES["aggregation"]:
        relationship_type = "Weak Aggregation"
        relationship = {"class_1": subject, "association_label": verb, "class_2": obj, "type": relationship_type}
    else:
        return []  # No relationship found

    # Return the relationship as a list containing the structured data
    return [relationship]

# Example sentences to test the function
sentences = [
    "Library contains Books.",
    "Library has Journals.",
    "Chapter is a part of Book.",
    "Department comprises Employees.",
    "Order includes Items.",
    "Each librarian can belong to one section.",
    "Each librarian belongs to a section."
]

# Collect results for each sentence
results = []
for sentence in sentences:
    result = identify_relationship(sentence)
    results.extend(result)

# Print final results
for item in results:
    print(item)
