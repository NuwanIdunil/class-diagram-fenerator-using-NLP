import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import re

from relcl import split_sentences_with_relcl
from sentpattern import filter_and_split_sentences
from sentpattern1 import filter_and_split_sentences1
from sentpattern2 import filter_and_split_sentences2
from suchas import split_sentences_with_such_as




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
        sentence1=remove_comma_before_conjunctions(sentence) 
        sentence1 = ' '.join(sentence1.split())
       
        doc = nlp(sentence1)
        tokens = [token.text for token in doc]
        tagged = [(token.text, token.tag_,token.dep_) for token in doc]
        root=[i for i, token in enumerate(doc) if token.dep_ == 'ROOT' and token.pos_ == 'VERB']
        rootverb=tokens[root[0]]  if root else ""
     
        # Identify positions of verbs and coordinating conjunctions
        verbs = [i for i, token in enumerate(doc) if token.dep_ == 'ROOT' or (token.dep_ == 'conj' and token.pos_ == 'VERB')]
        conjunctions = [i for i, token in enumerate(doc) if (token.text.lower() == 'and' or token.text == ',') and token.head.text == rootverb]
       
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
        if and_index + 1 < len(tokens) and (tagged[and_index + 1][1].startswith('VB') or tagged[and_index + 1][1].startswith('MD') ):
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
    connectives = {'and', 'or', 'but', 'yet',','}
    verbs = [token.i for token in doc if token.dep_ == "ROOT"]
    if len(verbs) == 1:
        verb_index = verbs[0]
        connectives = {'and', 'or', 'but', 'yet',','}
        connective_indices = [token.i for token in doc if token.text.lower() in connectives and token.i > verb_index]
    
    
    # Check for exactly one verb and at least one connective
    if len(verbs) == 1 and len(connective_indices) >= 1:
        return True
    return False

# Function to split sentences based on multiple objects and connectives
def split_sentence_by_multiple_objects(sentences):
    connectives = {'and', 'or', 'but', 'yet', ','}
    final_out = []
    
    for sentence in sentences:
        sentence = re.sub(r'(?<!\band\b)\s*,\s*(?!\band\b)', ' and ', sentence)
    
    # Remove the comma if there is an "and" word before or after it
        sentence = re.sub(r'\band\s*,\s*', ' and ', sentence)
        sentence = re.sub(r'\s*,\s*and\b', ' and ', sentence)
    
    # Remove any consecutive "and and" that might be generated
        sentence = re.sub(r'\band\s+and\b', 'and', sentence)
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        doc = nlp(sentence)
        new_sentences = []
        isthismatched=False
        if not matches_pattern(doc):
            final_out.append(sentence)
           
            continue
       
        verb_token = next((token for token in doc if token.dep_ == "ROOT"), None)
        if not verb_token:
            final_out.append(sentence)
            continue
        
        verb_index = verb_token.i
        connective_indices = [token.i for token in doc if token.text.lower() in connectives and token.i > verb_index]
        if not connective_indices:
            final_out.append(sentence)
            continue
        
        # Get subject and middle part between verb and first connective
        subject = " ".join([token.text for token in doc[:verb_index]])
        verb = verb_token.text
        middle_part = " ".join(token.text for token in doc[verb_index + 1:connective_indices[0] - 1])
      
        previous_index = verb_index
        is_first_sentence = True

        # Identify a relevant preposition that is a direct child of the root verb
        preposition_index = next(
            (token.i for token in doc[previous_index + 1:] if (token.dep_ in {"prep", "aux","agent"} and token.head == verb_token)),
            None
        )
        if not preposition_index:
            preposition_index=0

        preposition = " ".join([token.text for token in doc[preposition_index:]]) if preposition_index else ""
       
      
        for connective_index in connective_indices:
          if connective_index < preposition_index or preposition_index ==0:
           
            object_part = " ".join([token.text for token in doc[previous_index + 1:connective_index]])
            isthismatched=True
            # Attach preposition only if it's within the range and directly linked to the root verb
            if preposition_index:
                object_part = f"{object_part} {preposition}"
               
            if is_first_sentence:
                new_sentences.append(f"{subject} {verb} {object_part}.")
                is_first_sentence = False
            else:
                new_sentences.append(f"{subject} {verb} {object_part}.")
            
            previous_index = connective_index

        # Handle the last part of the sentence
        object_part = " ".join([token.text for token in doc[previous_index + 1:]])
        
        
        new_sentences.append(f"{subject} {verb} {object_part}")
        
        
        final_out.extend(new_sentences)
        if not isthismatched:
           final_out.append(sentence)
    
    return final_out


def split_sentence_by_multiple_objects_pre(sentences):
    connectives = {'and', 'or', 'but', 'yet', ','}
    final_out = []
    
    for sentence in sentences:
        sentence = re.sub(r'(?<!\band\b)\s*,\s*(?!\band\b)', ' and ', sentence)
    
    # Remove the comma if there is an "and" word before or after it
        sentence = re.sub(r'\band\s*,\s*', ' and ', sentence)
        sentence = re.sub(r'\s*,\s*and\b', ' and ', sentence)
    
    # Remove any consecutive "and and" that might be generated
        sentence = re.sub(r'\band\s+and\b', 'and', sentence)
        doc = nlp(sentence)
        new_sentences = []
        isthismatched=False
   
        if not matches_pattern(doc):
            final_out.append(sentence)
           
            continue
        
        verb_token = next((token for token in doc if token.dep_ == "ROOT"), None)
        if not verb_token:
            final_out.append(sentence)
            continue
        
        verb_index = verb_token.i
        connective_indices = [token.i for token in doc if token.text.lower() in connectives and token.i > verb_index]
        if not connective_indices:
            final_out.append(sentence)
            continue
    
        # Get subject and middle part between verb and first connective
        subject = " ".join([token.text for token in doc[:verb_index]])
        verb = verb_token.text
        previous_index = verb_index
        is_first_sentence = True

        # Identify a relevant preposition that is a direct child of the root verb
        preposition_index = next(
        (token.i for token in reversed(doc[previous_index + 1:]) if token.dep_ in {"prep", "aux", "agent"}),
        None
        )

        if not preposition_index:
           preposition_index=50

        preposition = " ".join([token.text for token in doc[preposition_index:]]) if preposition_index else ""
     
        if preposition_index:
         middle_part = " ".join(token.text for token in doc[verb_index + 1 : preposition_index+1])
         
         
         for connective_index in connective_indices:
          if connective_index > preposition_index:
          
            object_part = " ".join([token.text for token in doc[previous_index + 1:connective_index]])
            isthismatched=True
            if is_first_sentence:
                new_sentences.append(f"{subject} {verb} {object_part}.")
                is_first_sentence = False
            else:
                new_sentences.append(f"{subject} {verb} {middle_part} {object_part}.")
            
            previous_index = connective_index

         if previous_index > preposition_index: 
         # Handle the last part of the sentence
          object_part = " ".join([token.text for token in doc[previous_index + 1:]])
          
          new_sentences.append(f"{subject} {verb} {middle_part} {object_part}")
        final_out.extend(new_sentences)
        if not isthismatched:
           final_out.append(sentence)
        
          
        
        
    
 
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
    pattern = re.compile(r'(?<=\.)\s+')
    
    # Split the paragraph using the pattern
    sentences = pattern.split(paragraph)
    return sentences

# Example usage:


import re


def replace_comma(sentence):
    # Replace commas with "and" if there are no "and" words before or after the comma
    #sentence = re.sub(r'(?<!\band\b)\s*,\s*(?!\band\b)', ' and ', sentence)
    
    # Remove the comma if there is an "and" word before or after it
    sentence = re.sub(r'\band\s*,\s*', ' and ', sentence)
    sentence = re.sub(r'\s*,\s*and\b', ' and ', sentence)
    
    # Remove any consecutive "and and" that might be generated
    sentence = re.sub(r'\band\s+and\b', 'and', sentence)

    return sentence

def remove_comma_before_conjunctions(sentence):
    # Define a regular expression pattern to match a comma followed by a space and one of the conjunctions
    pattern = re.compile(r',\s*(and|or|but|yet|,)')
    # Substitute the matched pattern with the conjunction (without the comma)
    sentence = pattern.sub(r' \1', sentence)
    return sentence

def process_sentences(sentences):
    return [replace_comma(sentence) for sentence in sentences]

import spacy
def remove_adverbs(paragraph):
    # Process the paragraph with SpaCy
    doc = nlp(paragraph)
    
    # Initialize a list to hold the filtered tokens and a flag to skip tokens
    filtered_tokens = []
    skip_next = False

    # Iterate through tokens
    for i, token in enumerate(doc):
        # Skip the token if the previous one was an adverb followed by a comma
        if skip_next:
            skip_next = False
            continue

        # If token is an adverb and followed by a comma, skip both
        if token.tag_ == "RB":
            if i + 1 < len(doc) and doc[i + 1].text == ",":
                skip_next = True  # Skip the comma in the next iteration
            continue
        
        if token.text.lower() == "assists":
            filtered_tokens.append("helps" + token.whitespace_)
            
        else:
            # Append non-adverb and non-comma tokens, preserving whitespace
            filtered_tokens.append(token.text + token.whitespace_)

    # Join the filtered tokens into a paragraph
    filtered_text = "".join(filtered_tokens)
   
    return filtered_text

def clean_sentences(sentences, remove_extra_spaces=False):
    cleaned_sentences = []
    
    for sentence in sentences:
        # Replace specified substrings
        
        sentence = sentence.rstrip('.')
        sentence += '.'

        sentence = sentence.replace(" ,", ",").replace(" 's", "'s")
        
        # Ensure space after period if needed
        sentence = re.sub(r'\.(?=\S)', '. ', sentence)

        # Optionally remove extra spaces
        if remove_extra_spaces:
            sentence = ' '.join(sentence.split())
        
        cleaned_sentences.append(sentence)

    return cleaned_sentences



def clean_sentences1(text, remove_extra_spaces=False):
    # Split the input text into sentences using a regex pattern
    sentences = re.split(r'(?<=[.!?]) +', text)  # This splits by punctuation followed by a space
    
    cleaned_sentences = []
    
    for sentence in sentences:
        # Replace specified substrings
        sentence = sentence.rstrip('.')
        sentence += '.'
        sentence = sentence.replace(" ,", ",").replace(" 's", "'s")
        
        # Ensure space after period if needed
        sentence = re.sub(r'\.(?=\S)', '. ', sentence)

        # Optionally remove extra spaces
        if remove_extra_spaces:
            sentence = ' '.join(sentence.split())
        
        # Remove any extra periods and ensure one period at the end
      

        cleaned_sentences.append(sentence)

    # Join the cleaned sentences into a single string
    cleaned_text = ' '.join(cleaned_sentences)

    return cleaned_text


# Example usage





# Example usage
paragraph = "A library issues loan item to customers .Each customer is known as member and is issued a membership card that shows unique member number."

# Reconstruct the paragraph without adverbs (RB)
filtered_text = remove_adverbs(paragraph)
filtered_text = clean_sentences1(filtered_text)
sentences = custom_sent_tokenize(filtered_text)
modified_sentences=clean_sentences(sentences)
#modified_sentences=split_sentences_with_such_as(modified_sentences)
modified_sentences=split_sentences_with_relcl(modified_sentences)

modified_sentences=filter_and_split_sentences(modified_sentences)
modified_sentences=filter_and_split_sentences1(modified_sentences)
modified_sentences=clean_sentences(modified_sentences)

modified_sentences=filter_and_split_sentences2(modified_sentences)
# print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

# # # #Apply the split_sentence_by_conjunction function
result = process_sentences(modified_sentences)
modified_sentences=split_sentence_by_multiple_subject(result)
modified_sentences = split_sentence_by_conjunction(modified_sentences)

modified_sentences = split_sentence_by_multiple_objects_pre(modified_sentences)
modified_sentences = split_sentence_by_multiple_objects(modified_sentences)
modified_sentences = split_sentence_by_conjunction(modified_sentences)
print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

for sent in modified_sentences:
   print(sent)

