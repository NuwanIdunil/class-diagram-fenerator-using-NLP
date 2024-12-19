import re
import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")



# Function to find and split sentences containing the phrase 'such as'
def split_sentences_with_such_as(text):
    # Process the text with spaCy
 
    
    # List to hold the resulting sentences
    resulting_sentences1 = []
    
    # Iterate through sentences in the document
    for sent in text:
        sent = nlp(sent)
        resulting_sentences = []
        # Check if 'such as' is in the sentence
        if "such as" in sent.text.lower():
            main_part, examples_part = sent.text.split("such as", 1)
            # Split the sentence at 'such as'
            # Clean up the main part
            main_part = main_part.strip().rstrip(',',)
            resulting_sentences.append(main_part + ".")  # Append the main sentence
            
            # Extract the direct object (dobj) using dependency parsing
            category = None
            for token in sent:
                if token.dep_ == "prep" and token.text=="as":  # Find the direct object
                    category = token.head
                    break
          


            if not category:
                # If no direct object found, look for the subject as a fallback
                for token in sent:
                    if token.dep_ == "nsubj":  # Find the subject
                        category = token.text
                        break
            if not category:
                  for token in sent:
                    if token.dep_ == "attr":  # Find the direct object
                     category = token.text
                     break

            if category is None:
                category = "examples"  # Fallback if no category found

            # Process examples, splitting by commas
            examples = examples_part.strip().split(',')
            examples = [ex.strip() for ex in examples]  # Clean whitespace
           
            # Flatten the examples list and handle conjunctions
            flat_examples = []
            for example in examples:
                if 'and' in example:  # Split by 'and'
                    items = example.split('and')
                   
                    flat_examples.extend([item.strip() for item in items if item.strip()])
                if 'or' in example:
                    print(example)
                    items = example.split('or')
                    
                    flat_examples.extend([item.strip() for item in items if item.strip()])
                else:
                    flat_examples.append(example.strip())

            # Generate sentences for each example
            for example in flat_examples:
                if example:  # Ensure it's not empty
                    # Remove any trailing punctuation for the example
                    example = example.rstrip('.!?,')
                    example_doc = nlp(example)
                    if not example_doc[0].tag_ in ["DT", "NN", "NNS", "NNP", "NNPS"]:  # Determiners or nouns
                        continue
                  
                    resulting_sentences.append(f"{example.capitalize()} is a {category}.")

                    for token in sent:
                        if token.dep_ == "relcl": 
                         if token.head.text in examples_part:
                               remaining_part = " ".join([t.text for t in sent if t.i > token.i])  # Everything after the relative clause
                               new_sentence = f"{example.capitalize()} {token.text} {remaining_part.strip()}"
                               resulting_sentences.append(new_sentence.strip())

                        # prep_phrase = ""  
                        # if token.dep_ == "ROOT": 
                        #         root = token.text
                        #         subject = " ".join([t.text for t in token.lefts])
                        #         for child in token.children:
                        #             if child.dep_== "prep":
                        #                 prep_phrase = " ".join([child.text] + [t.text for t in child.subtree if t != child])
                
                        # if prep_phrase and len(resulting_sentences) > 1:
                        #   new_sentence = f"{subject} {root} {example.capitalize()} {prep_phrase} "
                        #   resulting_sentences.append(new_sentence.strip())
                        
                    # Capitalize and format the new sentence based on the category
                   
        else:
            # If not containing 'such as', add the sentence as is
            resulting_sentences.append(sent.text.strip())
    
       
        
        resulting_sentences1.extend(resulting_sentences)
                       

    return resulting_sentences1

text = [
" Each order contains details such as the order ID, the list of books purchased, the total amount, and the order status."
]
resulting_sentences = split_sentences_with_such_as(text)
print("Resulting sentences:")
for sentence in resulting_sentences:
    print("-", sentence)
