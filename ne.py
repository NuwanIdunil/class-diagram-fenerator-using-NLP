import re

# Updated regex pattern
attribute_pattern = (
    r"^(?:(?:The|Each|A|An|These|Those|This|That)\s*)?"  # Optional determiner
    r"(attribute|attributes|property|properties|feature|features|item|items|detail|details)\s+"  # Singular/plural nouns
    r"(have|has|include|possess|contain)\s+"  # Match verbs
    r"([\w\s,]+)\.$"  # Capture attributes list
)

# Test sentences
sentences = [
    "The attributes include speed, durability, and cost.",
    "Attributes have high strength, flexibility, and toughness.",
    "These properties possess modularity, usability, and compatibility.",
    "Those details contain dimensions, weight, and color.",
    "This item has portability and versatility.",
    "An attribute has simplicity and efficiency."
]

# Matching loop
for sentence in sentences:
    match = re.match(attribute_pattern, sentence)
    if match:
        print(f"Sentence: {sentence}\nMatched attributes: {match.group(1)}")  # Adjusting to capture correct group
    else:
        print(f"Sentence: {sentence}\nNo match.")
