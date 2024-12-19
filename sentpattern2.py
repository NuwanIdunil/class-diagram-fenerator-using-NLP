import re
import spacy

def is_plural(token):
    """Determine if the word is plural based on its part of speech."""
    return token.tag_ == 'NNS'  # 'NNS' is the tag for plural nouns

def convert_word_to_singular(token):
    """Convert a plural word to singular if it's plural, otherwise return the same word."""
    if is_plural(token):
        return token.lemma_  # SpaCy's lemmatizer will convert plural to singular
    return token.text

def filter_and_split_sentences2(sentences):
    nlp = spacy.load("en_core_web_sm")
    # Define the pattern to identify sentences with any verb in the action description and optional identifiers
    pattern = r"(\b[\w\s]+\b) (\w+ [\w\s]+), identified by (.+)"
    
    # List to store the processed sentences
    processed_sentences = []
    
    # Loop through each sentence in the input list
    for sentence in sentences:
        # Check if the sentence matches the pattern
        match = re.search(pattern, sentence)
        
        if match:
            # Use SpaCy to parse the sentence
            doc = nlp(sentence)

            # Find the root index
            root = [token for token in doc if token.dep_ == 'ROOT']
            if root:  # Ensure there's a root found
                root_index = root[0].i
                
                # Extract entity up to the root index
                entity = " ".join(token.text for token in doc[:root_index]).strip()
                action = match.group(2).strip()        # e.g., "assists in managing school activities"
                identifiers = match.group(3).strip()   # e.g., "their staff ID, name, and department"
                action1 = match.group(2).strip()
                entity1 = match.group(1).strip()
                
                # Create the main sentence for the entity and action
                processed_sentences.append(f"{entity1} {action}.")
                
                # Split the identifiers by commas and "and" and create individual sentences for each identifier
                for identifier in re.split(r',\s*|\s*and\s+', identifiers):  # Improved splitting by handling whitespace around 'and'
                    identifier = identifier.strip()
                    if identifier:  # Avoid empty strings from any extra splits
                        processed_sentences.append(f"{entity} is identified by {identifier}.")
            else:
                # If no root found, add the original sentence
                processed_sentences.append(sentence)
        else:
            # If no match, add the sentence as-is to the processed list
            processed_sentences.append(sentence)
    
    return processed_sentences



# # Example usage
# sentences = [
#     #"Administrative staff assists in managing library activities, identified by their staff ID, name.",
#     "Administrative staff assists in managing library activities, identified by their staff ID, name.",
# ]

# split_sentences = filter_and_split_sentences2(sentences)
# print(split_sentences)
