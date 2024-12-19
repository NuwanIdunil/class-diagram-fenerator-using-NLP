import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

def is_plural(token):
    """Determine if the word is plural based on its part of speech."""
    return token.tag_ == 'NNS'  # 'NNS' is the tag for plural nouns

def convert_word_to_singular(token):
    """Convert a plural word to singular if it's plural, otherwise return the same word."""
    if is_plural(token):
        return token.lemma_  # SpaCy's lemmatizer will convert plural to singular
    return token.text

# Sample sentEach teacher can belong to one department and student can manage multiple courses for different students.ence
sentence =  "The library keeps other member's details ."
           
# Process the sentence
sentence = nlp(sentence)
 

for token in sentence:
    children_text = ", ".join([child.text for child in token.children])
    print(f"{token.text:<10} {token.tag_:<10} {token.pos_:<15} {token.dep_:<15} {token.head.text:<15} {children_text}")
