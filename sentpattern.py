import re

def filter_and_split_sentences(sentences):
    # Define the pattern to identify sentences with or without location descriptions
    pattern = r"(\b\w+\b) are (\b\w+\b)(?: registered at the (\b\w+\b))? and identified by (.+)|(\b\w+\b) are (\b\w+\b) identified by (.+)"
    
    # List to store the processed sentences
    processed_sentences = []
   
    # Loop through each sentence in the input list
    for sentence in sentences:
        # Check if the sentence matches the pattern
        match = re.search(pattern, sentence)
        
        if match:
            # Extract components of the sentence for both types of sentence structures
            if match.group(1):  # For sentences with "registered at"
                entity = match.group(1)
                description = match.group(2)
                location = match.group(3)
                attributes = match.group(4)
                
                # Create the first part of the split sentence if location is present
                processed_sentences.append(f"{entity} are {description} registered at the {location}.")
            else:  # For sentences without "registered at"
                entity = match.group(5)
                description = match.group(6)
                attributes = match.group(7)
            
            # Split the attributes by "and" and create individual sentences for each attribute
            for attribute in attributes.split(" and "):
                processed_sentences.append(f"{entity} are identified by {attribute.strip()}.")
        else:
            # If no match, add the sentence as-is to the processed list
            processed_sentences.append(sentence)
   
    return processed_sentences

# # # Example usage
# sentences = [
#     "Administrative staff assists in managing library activities, identified by their staff ID, name",
    
# ]

# split_sentences = filter_and_split_sentences(sentences)
# print(split_sentences)
