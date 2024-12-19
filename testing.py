import spacy

# Load the SpaCy language model
nlp = spacy.load("en_core_web_sm")

def remove_until_word(sentence, target_word):
    doc = nlp(sentence)
    start_index = 0
    
    # Find the position of the target word
    for i, token in enumerate(doc):
        if token.text.lower() == target_word.lower():
            start_index = i + 1  # Start after the target word
            break

    # Rebuild the sentence from the word after the target word onward
    return " ".join([token.text for token in doc[start_index:]])

# Example usage
sentence = "In this system, each Book has attributes like a title, author, ISBN, publisher, and publication year."
cleaned_sentence = remove_until_word(sentence, "system")
print(cleaned_sentence)
