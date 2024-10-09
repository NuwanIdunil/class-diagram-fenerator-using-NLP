import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import re


# Tokenize and tag function
def tokenize_and_tag(sentence):
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    return tokens, tagged

# Function to split sentences based on conjunctions
import spacy

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def split_sentence_by_conjunction(sentences):
    new_sentences = []
    
    for sentence in sentences:
        doc = nlp(sentence)
        tokens = [token.text for token in doc]
        tagged = [(token.text, token.tag_,token.dep_) for token in doc]
        root=[i for i, token in enumerate(doc) if token.dep_ == 'ROOT' and token.pos_ == 'VERB']

        # Identify positions of verbs and coordinating conjunctions
        verbs = [i for i, token in enumerate(doc) if token.dep_ == 'ROOT' or (token.dep_ == 'conj' and token.pos_ == 'VERB')]
        conjunctions = [i for i, token in enumerate(doc) if token.text.lower() == 'and' or token.text == ',']
        object = [i for i, token in enumerate(doc) if token.dep_ == 'dobj']
        all_verbs=[ i for i, token in enumerate(doc) if token.pos_ == 'VERB']
        preposition=[]
        if len(all_verbs)>2:
         preposition =[i for i, token in enumerate(doc[verbs[0]: all_verbs[1]+1]) if ((token.dep_ == 'xcomp' or token.dep_ == 'ccomp') and token.pos_ == 'VERB')]
        # Ensure we have at least one verb and one conjunction
        if len(verbs) < 2 or len(conjunctions) < 1:
            new_sentences.append(sentence)
            continue
        
        # Find the positions of the first and second verbs
        first_verb_index = verbs[0]
        second_verb_index = verbs[1]

        # Split the sentence at the conjunction 'and'
        and_index = conjunctions[0]
        
        # Extract parts of the sentence
        


        
        S = " ".join(tokens[:first_verb_index])  # Subject
        V1 = tokens[first_verb_index]           # First verb
        if and_index + 1 < len(tokens) and tagged[and_index + 1][1].startswith('VB'):
            if  tagged[ first_verb_index + 1][0] == 'and':
              O1 = " ".join(tokens[second_verb_index + 1:])  
            else:
              O1 = " ".join(tokens[first_verb_index + 1:and_index])  # First object
        elif tagged[second_verb_index - 1][0] == 'and':
            O1 = " ".join(tokens[first_verb_index + 1:second_verb_index - 1])  
        else:
            O1 = " ".join(tokens[first_verb_index + 1:and_index]) 
            new_sentences.append(f"{S} {V1} {O1}.")
            remain = " ".join(tokens[and_index + 1:]) 
            new_sentences.append(f"{remain}.")
            continue
        
       
            
        third_verb_index = all_verbs[1]
       
        if len(preposition) > 0 and len(all_verbs) >=2:
             S2 = " ".join(tokens[:third_verb_index])
             V2 = tokens[second_verb_index] 
             O2 = " ".join(tokens[second_verb_index + 1:])      
        else:
             S2 = " ".join(tokens[:first_verb_index])
             V2 = tokens[second_verb_index]          # Second verb
             O2 = " ".join(tokens[second_verb_index + 1:])  # Second object
        
        # Construct new sentences
        new_sentences.append(f"{S} {V1} {O1}.")
        new_sentences.append(f"{S2} {V2} {O2}.")
    
    return new_sentences


# Function to split sentences based on the specified rule

def matches_pattern(doc):
    connectives = {'and', 'or', 'but', 'yet'}
    verbs = [token.i for token in doc if token.dep_ == "ROOT"]
    if len(verbs) == 1:
        verb_index = verbs[0]
        connectives = {'and', 'or', 'but', 'yet'}
        connective_indices = [token.i for token in doc if token.text.lower() in connectives and token.i > verb_index]
    
    
    # Check for exactly one verb and at least one connective
    if len(verbs) == 1 and len(connective_indices) >= 1:
        return True
    return False

# Function to split sentences based on multiple objects and connectives
def split_sentence_by_multiple_objects(sentences):
    connectives = {'and', 'or', 'but', 'yet',','}
    final_out=[]
    
    for sentence in sentences:
        doc = nlp(sentence)
        new_sentences = []
        # Check if the sentence matches the pattern
        if not matches_pattern(doc):
            final_out.append(sentence)
            continue
        
        # Identify the position of the verb and connectives
        verb_index = next(token.i for token in doc if token.dep_ == "ROOT")
        connective_indices = [token.i for token in doc if token.text.lower() in connectives  and token.i > verb_index]

        # Find the subject and verb
        subject = " ".join([token.text for token in doc[:verb_index]])
        verb = doc[verb_index].text
        if doc[connective_indices[0]-2].dep_ == "compound":
         midle_part =" ".join(token.text for token in doc[verb_index + 1:connective_indices[0]-2] )
        else:
         midle_part =" ".join(token.text for token in doc[verb_index + 1:connective_indices[0]-1] )
        # Split the sentence at each connective and construct new sentences
        previous_index = verb_index 
        

        
        is_first_sentence = True
        for connective_index in connective_indices:
        
         object_part = " ".join([token.text for token in doc[previous_index + 1:connective_index]])
    
         if is_first_sentence:
          new_sentences.append(f"{subject} {verb} {object_part}")
          is_first_sentence = False
         else:
          new_sentences.append(f"{subject} {verb} {midle_part} {object_part}")
    
         previous_index = connective_index

        # Add the last part of the sentence as the final object
    
        object_part = " ".join([token.text for token in doc[previous_index + 1:]])
        
        new_sentences.append(f"{subject} {verb} {midle_part} {object_part}.")
        preposition_index = next((token.i for token in doc[previous_index + 1:] if token.dep_ == "prep" or token.dep_ == "aux" ), 0)
        if preposition_index > 0:
            preposition = " ".join([token.text for token in doc[preposition_index:]])
            
            length = len(new_sentences)
            for i in range(length-1):
                new_sentences[i] = new_sentences[i] + " " + preposition
                final_out.append (new_sentences[i])
            final_out.append (f"{subject} {verb} {midle_part} {object_part}")
        else:
          for sentence in new_sentences:
                final_out.append (sentence)
               
    return final_out



def matches_pattern_multiple_subject(doc):
    verbs = [token.i for token in doc if token.pos_ == "VERB"]
    connectives = {'and', 'or', 'but', 'yet'}
    verbs = [token.i for token in doc if token.pos_ == "VERB"]
    if len(verbs) == 1:
        verb_index = verbs[0]
        connectives = {'and', 'or', 'but', 'yet'}
        connective_indices = [token.i for token in doc if token.text.lower() in connectives and token.i < verb_index]
    
    
    # Check for exactly one verb and at least one connective
    if len(verbs) == 1 and len(connective_indices) >= 1:
        return True
    return False

# Function to split sentences based on multiple objects and connectives
def split_sentence_by_multiple_subject(sentences):
    connectives = {'and', 'or', 'but', 'yet'}
    new_sentences = []

    for sentence in sentences:
        doc = nlp(sentence)
        
        # Check if the sentence matches the pattern
        if not matches_pattern_multiple_subject(doc):
            new_sentences.append(sentence)
            continue

        # Identify the position of the verb and connectives
        verb_index = next(token.i for token in doc if token.pos_ == "VERB")

        connective_indices = [token.i for token in doc if token.text.lower() in connectives  and token.i < verb_index]
        previous_connective_index=-1
        # Find the subject and verb
        aux=""
        auxhas=False
        if doc[verb_index -1].dep_=="aux":
            aux= "is"
            auxhas= True
        for connective_index in connective_indices:
          subject1 = " ".join([token.text for token in doc[previous_connective_index+1:connective_index]])
          ramin= " ".join([token.text for token in doc[verb_index+1: ]])
          verb = doc[verb_index].text 
          new_sentences.append(f"{subject1} {aux} {verb} {ramin}.")
          previous_connective_index=connective_index
        if auxhas :
         subject = " ".join([token.text for token in doc[connective_index+1:verb_index]])
         new_sentences.append(f"{subject} {verb} {ramin}.")
        else:
           subject = " ".join([token.text for token in doc[connective_index+1:verb_index]])
           new_sentences.append(f"{subject} {verb} {ramin}.")
    return new_sentences


def custom_sent_tokenize(paragraph):
    # Regular expression to identify sentence boundaries
    pattern = re.compile(r'(?<=\.)\s*(?=[A-Z])')
    
    # Split the paragraph using the pattern
    sentences = pattern.split(paragraph)
    return sentences

# Example usage:


import re


# def replace_comma(sentence):
#     # Replace commas with "and" if there are no "and" words before or after the comma
#     sentence = re.sub(r'(?<!\band\b)\s*,\s*(?!\band\b)', ' and ', sentence)
    
#     # Remove the comma if there is an "and" word before or after it
#     sentence = re.sub(r'\band\s*,\s*', ' and ', sentence)
#     sentence = re.sub(r'\s*,\s*and\b', ' and ', sentence)
    
#     # Remove any consecutive "and and" that might be generated
#     sentence = re.sub(r'\band\s+and\b', 'and', sentence)

#     return sentence

def remove_comma_before_conjunctions(sentence):
    # Define a regular expression pattern to match a comma followed by a space and one of the conjunctions
    pattern = re.compile(r',\s*(and|or|but|yet|,)')
    # Substitute the matched pattern with the conjunction (without the comma)
    sentence = pattern.sub(r' \1', sentence)
    return sentence

def process_sentences(sentences):
    return [remove_comma_before_conjunctions(sentence) for sentence in sentences]

# Example usage
paragraph ="The library identifies each book by a title, an author, and an ISBN number"
sentences = custom_sent_tokenize(paragraph)
result = process_sentences(sentences)


# Apply the split_sentence_by_conjunction function
modified_sentences = split_sentence_by_conjunction(result)
# modified_sentences = split_sentence_by_multiple_subject(modified_sentences)
modified_sentences = split_sentence_by_multiple_objects(modified_sentences)
# modified_sentences = split_sentence_by_conjunction(modified_sentences)
for sentence in modified_sentences:            
    print(sentence)
    


