import re
import spacy
nlp = spacy.load("en_core_web_sm")

def extract_classes_and_attributes(sentences):
    # Regex pattern to match "subject + verb identifies + object" with compound nouns
    pattern = r"^(?:A|The|An)\s+(.*?)\sidentifies\s(?:a|the|an|these|those)?\s*([\w\s]+)(?:s)?\."

    # List to store identified classes and attributes
    classes = []
    matched_sentences = []
    remaining_sentences = []

    # Function to strip leading determiners from the subject
    def strip_determiners(attribute):
        determiners = ["a", "an", "the", "these", "those"]
        words = attribute.split()
        if words and words[0].lower() in determiners:
            words = words[1:]  # Remove the determiner
        return " ".join(words)

    # Function to remove leading determiners from class names
    def strip_class_determiners(class_name):
        determiners = ["each", "a", "an", "the", "this", "these", "those"]
        words = class_name.split()
        if words and words[0].lower() in determiners:
            words = words[1:]  # Remove the determiner
        return " ".join(words)

    # Process each sentence
    for sentence in sentences:
        match = re.search(pattern, sentence)
        if match:
            # Extract the subject (attribute) and object (class entity)
            attribute_phrase = match.group(1).strip()
            class_entity = match.group(2).strip()

            # Clean up the attribute phrase
            attribute = strip_determiners(attribute_phrase)

            # Clean up the class entity (e.g., if "librarians" -> "librarian")
            class_name = class_entity.rstrip('s')  # Remove trailing 's' for plural

            # Store class and attribute in the classes list
            classes.append({"classname": class_name, "attributes": [attribute]})
            
            # Add matched sentence to the matched_sentences list
            matched_sentences.append(sentence)
        else:
            # If the sentence didn't match, add it to the remaining_sentences list
            remaining_sentences.append(sentence)



    return remaining_sentences, matched_sentences

# Sample text input


# Split the text into sentences using SpaCy

# sentences = [
#     "The car identifies a vehicle.",
 
# ]

# # Call the function
# remaining, matched = extract_classes_and_attributes(sentences)

# # Output the results
# print("Remaining Sentences:", remaining)
# print("Matched Sentences:", matched)
# # # Call the function and get the resultsremaining_sentences, matched_sentences = extract_classes_and_attributes(sentences)


