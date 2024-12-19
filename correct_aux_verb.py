import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def correct_aux_verb(sentence):
    doc = nlp(sentence)
    corrected_tokens = []
    
    for i, token in enumerate(doc):
        if token.text in {"is", "are"}:
            # Check if the next token exists and its POS tag
            if i + 1 < len(doc) and doc[i + 1].tag_ in {"VBG", "VBD", "NOUN","VBN"}:
                corrected_tokens.append(token.text)  # Keep the auxiliary
            # Otherwise, skip the auxiliary
        else:
            corrected_tokens.append(token.text)  # Add other words unchanged
    
    return " ".join(corrected_tokens)

# Example sentence
sentence = "Each section is has students who buy books ."
print(correct_aux_verb(sentence))
