import re

def extract_classes_and_attributes(sentences):
    # Regex pattern to match "subject + verb identifies + object + using/by + attribute"
    pattern = r"^(?:The|A|An)\s+(\w+)\s+identifies\s+(?:a|the|an)?\s*(\w+\s*\w*)\s+(?:using|by)\s+(.*)\.$"

    # List to store identified classes and attributes
    classes = []

    # Function to strip leading determiners from the attribute
    def strip_determiners(attribute):
        determiners = ["a", "an", "the", "these", "those", "their"]
        words = attribute.split()
        if words and words[0].lower() in determiners:
            words = words[1:]  # Remove the determiner
        return " ".join(words)  # Return the cleaned attribute

    # Function to remove leading determiners from class names
    def strip_class_determiners(class_name):
        determiners = ["each", "a", "an", "the", "this", "these", "those"]
        words = class_name.split()
        if words and words[0].lower() in determiners:
            words = words[1:]  # Remove the determiner
        return " ".join(words)  # Return the cleaned class name

    # Process each sentence
    for sentence in sentences:
        match = re.search(pattern, sentence)
        if match:
            # Extract the subject, object, and attribute information
            subject = match.group(1).strip()  # Subject entity
            object_entity = match.group(2).strip()  # Object class
            attribute_phrase = match.group(3).strip()  # Attribute information
            
            # Clean up the attribute phrase
            attribute = strip_determiners(attribute_phrase)
            
            # Clean up the object entity (e.g., if "users" -> "user")
            class_name = object_entity.rstrip('s')  # Remove trailing 's' for plural

            # Store class and attribute in the classes list
            classes.append({"classname": class_name, "attributes": [attribute]})

    return classes  # Return the list of identified classes and attributes

# # Sample sentences
# sentences = [
#   "Administrative staff assists in managing library activities, identified by their staff ID, name"
# ]

# # Call the function and print the results
# identified_classes = extract_classes_and_attributes(sentences)
# for cls in identified_classes:
#     print(f"Class: {cls['classname']}, Attributes: {', '.join(cls['attributes'])}")
