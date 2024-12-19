import re

def process_sentences(sentences):
    # Updated regex pattern to match "is identified by" or "are identified by"
    pattern = r"(?:\w+(?:\s+\w+)*)?\s+(?:is|are)\s+(?:\w+\s+)?identified\s+by\s+(.*)"
    
    # Lists to store matched and remaining sentences
    matched_sentences = []
    remaining_sentences = []

    # Process each sentence
    for sentence in sentences:
        match = re.search(pattern, sentence)
        if match:
            matched_sentences.append(sentence)
        else:
            remaining_sentences.append(sentence)

    # Return the results
    return remaining_sentences, matched_sentences

# # Sample sentences
# sentences = [
#     "The car identifies a vehicle.",
 
# ]

# # Call the function
# remaining, matched = process_sentences(sentences)

# # Output the results
# print("Remaining Sentences:", remaining)
# print("Matched Sentences:", matched)
