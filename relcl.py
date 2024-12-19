# Load the English NLP model
import spacy
nlp = spacy.load("en_core_web_sm")

def split_sentences_with_relcl(text):
    # List to hold the resulting sentences
    resulting_sentences = []
    
    # Iterate through sentences in the document
    for sent in text:
        subject = ""
        sent = nlp(sent)
        ismatched = False
        root_index = None
        child_index = None
        
        for token in sent:
            if token.dep_ == "ROOT":
                root = token.text
                root_index = token.i
                
        for token in sent:         
            if token.pos_ == "VERB" and (token.dep_ == "relcl" or token.dep_ == "ccomp"):
                # Find the direct object     
                for child in token.children:  
                    if (child.dep_ == "nsubj" or  child.dep_ == "nsubjpass") and (child.tag_ == "WDT" or child.tag_ == "WP"):
                        child_index = child.i
                        if root_index < child_index:
                            if root == "is" or root == "are":
                                sentence1 = " ".join(token.text for token in sent[:child_index-1]) + "."
                                subject = " ".join(token.text for token in sent[:root_index])
                                setence2lastpart = " ".join(token.text for token in sent[child_index+1:])
                                sentence2 = f"{subject.capitalize()} {root} {setence2lastpart} "
                                resulting_sentences.append(sentence1.strip())
                                resulting_sentences.append(sentence2.strip())
                                ismatched = True
                                break
                            else:
                                subject_phrase = " ".join(token.text for token in sent[root_index+1:child_index-1]).rstrip(",").strip() 
                                sentence1 = " ".join(token.text for token in sent[:child_index-1]) + "."
                                setence2lastpart = " ".join(token.text for token in sent[child_index+1:])
                                sentence2 = f"{subject_phrase.capitalize()} {setence2lastpart} "
                                resulting_sentences.append(sentence1.strip())
                                resulting_sentences.append(sentence2.strip())
                                ismatched = True
                                break

        if not ismatched:
            resulting_sentences.append(sent.text.strip())

    # Remove any extra space before commas in resulting sentences
    resulting_sentences = [sentence.replace(" ,", ",").replace(" 's", "'s") for sentence in resulting_sentences]

    return resulting_sentences          

# # Example usage
# sentences = [
#     "Books can be borrowed by Members, who are registered with a unique membership ID, name, and contact information"
# ]

# resulting_sentences = split_sentences_with_relcl(sentences)
# print("Resulting sentences:")
# for sentence in resulting_sentences:
#     print("-", sentence)
