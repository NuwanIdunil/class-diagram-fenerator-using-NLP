import re

def filter_and_split_sentences1(sentences):
    # Define the pattern to identify sentences with entity descriptions and identifiers
    pattern = r"(\b\w+\b) are (\b[\w\s]+\b) identified by (.+)"
    
    # List to store the processed sentences
    processed_sentences = []
    
    # Loop through each sentence in the input list
    for sentence in sentences:
        # Check if the sentence matches the pattern
        match = re.search(pattern, sentence)
        
        if match:
            # Extract components of the sentence
            entity = match.group(1)           # e.g., "Librarians"
            description = match.group(2)      # e.g., "staff members"
            attributes = match.group(3)       # e.g., "librarian ID and name"
            
            # Create the base part of the sentence
            processed_sentences.append(f"{entity} are {description}.")
            
            # Split the attributes by "and" and create individual sentences for each attribute
            for attribute in attributes.split(" and "):
                processed_sentences.append(f"{entity} are identified by {attribute.strip()}.")
        else:
            # If no match, add the sentence as-is to the processed list
            processed_sentences.append(sentence)
    
    return processed_sentences

# # # # Example usage
# sentences = [
#     "Administrative staff assists in managing library activities, identified by their staff ID, name"
# ]

# split_sentences = filter_and_split_sentences1(sentences)
# print(split_sentences)
