import re
import spacy

import pattern2
import pattern3

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")
classes = []

def is_plural(token):
    """Determine if the word is plural based on its part of speech."""
    return token.tag_ == 'NNS'  # 'NNS' is the tag for plural nouns

def convert_word_to_singular(token):
    """Convert a plural word to singular if it's plural, otherwise return the same word."""
    if is_plural(token):
        return token.lemma_  # SpaCy's lemmatizer will convert plural to singular
    return token.text

# Paragraph to be split into sentences and analyzed
paragraph = """
A library issues loan items to customers.
A customer is a member.
The library issues a membership card to each member.
A membership card shows a unique member number.
The library keeps other member's details .
These details include member name.
These details include member address.
These details include member date of birth.
The library comprises subject sections.
A classification mark denotes each section.
A bar code identifies a loan item.
Two types of loan items exist.
These types are language tapes.
These types are books .
A language tape has a title.
A language tape has a language.
A language tape has a level.
A book has a title.
A book has an author.
A customer may borrow a maximum of eight items at one time.

"""

# Function to extract subject phrases from a sentence
def extract_subject_phrase(sentence):

    for token in sentence:
        if token.dep_ == "nsubj":  # Check if the token is a nominal subject
            subject_phrase = [convert_word_to_singular(token)]
            for child in token.children:
                if child.dep_ in ("compound", "amod"):
                    subject_phrase.append(convert_word_to_singular(child))
            subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
            subject_phrase = subject_phrase[::-1]
           
            return " ".join(subject_phrase)
    return ""

# Function to extract direct objects from a sentence
def  extract_from_Posses(sentence):
    subject = None
    direct_object = None

    for token in sentence:
        if token.dep_ == "nsubj":  # Check if the token is a nominal subject
            subject = token  # Assign the token directly as the subject

        elif token.dep_ == 'poss':
            direct_object = token.head
            subject = token  # Assign the token directly as the subject


    #Ensure subject and direct_object are singularized if they exist
    subject = convert_word_to_singular(subject) if subject else None
    direct_object = convert_word_to_singular(direct_object) if direct_object else None

    return subject, direct_object


def extract_from_direct_object(sentence):
    subjects = []
    for token in sentence:
        if token.dep_ == "ROOT":
            for child2 in token.children:
                # Check for specific prepositions
                if child2.dep_ == "prep" and child2.text in ["to", "of"]:
                    for child3 in child2.children:
                        if child3.dep_ == "pobj":
                            subjects.append(convert_word_to_singular(child3))
    return subjects

def extract_noun_phrases(sentence):
    noun_phrases = []
    for chunk in sentence.noun_chunks:

        nouns = [convert_word_to_singular(token) for token in chunk if token.pos_ == "NOUN" or token.dep_ == "amod"]
        if len(nouns) >= 2:
             noun_phrases.append((nouns[0], " ".join(nouns[1:])))

    return noun_phrases

def extract_hasa_relationship(sentence):
    hasa_relationships = []
    thishasrelcl=False
    relcl=None
   
    for token in sentence:
       
        if token.lemma_ in ("have", "has","include","possess","contain"):
           
            subject = None
            obj = None
            for child in token.children:

                if child.dep_ == "nsubj":  # Check if the token is a nominal subject
                 subject_phrase = [convert_word_to_singular(child)]
                 subject=convert_word_to_singular(child)
                 for child1 in child.children:
                    if child1.dep_ in ("compound", "amod"):
                      subject_phrase.append(convert_word_to_singular(child1))
                      subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
                      subject_phrase = subject_phrase[::-1]

                # Convert subject_phrase list into a single string
                      subject_text = " ".join(subject_phrase)
                      subject =subject_text

                elif child.dep_ in ("dobj", "attr"):
                    
                    obj = convert_word_to_singular(child)
                    additional_obj_parts = []
                    poss_part =[]
                    for child1 in child.children:
                        if child1.dep_ == "relcl":
                            relcl=child1.text
                            thishasrelcl=True
                          
                        if child1.dep_ in ("amod", "compound"):
                            additional_obj_parts.append(convert_word_to_singular(child1))
                        
                        if child1.dep_ in ("prep") :
                            for child2 in child1.children:
                                if child2.dep_ in ("dobj", "pobj"):
                                    obj=child2.text
                                    for child3 in child2.children:
                                        if child3.dep_ in ("amod", "compound"):
                                             additional_obj_parts.append(convert_word_to_singular(child3))
                    if additional_obj_parts:
                        obj = " ".join(additional_obj_parts) + " " + obj


            if subject and obj:

                hasa_relationships.append((subject, obj))
                
    return hasa_relationships ,relcl,thishasrelcl

def extract_object (sentence,classes):
    def read_nouns_from_files(file_paths):
        nouns = set()
        for file_path in file_paths:
            with open(file_path, 'r') as file:
                nouns.update(line.strip() for line in file)
        return nouns

    file_paths = ['corpus_Int.txt', 'corpus_String.txt', 'corpus_Double.txt']
    nouns_in_text = []
    subject = ""
    attributes=[]
    new_subject=""
    objfound=False
    nouns_in_files = read_nouns_from_files(file_paths)

    for token in sentence:
        if token.dep_ == "nsubj":  # Check if the token is a nominal subject
            subject_phrase = [convert_word_to_singular(token)]
            for child in token.children:
                if child.dep_ in ("compound", "amod"):
                    subject_phrase.append(convert_word_to_singular(child))
            subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
            subject_phrase = subject_phrase[::-1]
            subject = " ".join(subject_phrase)
        is_this_class=False
        if token.dep_ == "ROOT":
            for child in token.children:
                if child.dep_ == "dobj":
                   
                    if child.lemma_ in nouns_in_files:
                        objfound=True
                        nouns_in_text=[child.text]
                        for child1 in child.children:
                          if child1.dep_ in ("compound", "amod"):
                               for class_info in classes:
                                   if class_info["classname"] == child1.text:
                                       is_this_class=True
                                       subject=class_info["classname"]

                               nouns_in_text.append(convert_word_to_singular(child1))
                        common_nouns = sorted(nouns_in_text, key=lambda x: sentence[token.i].i)
                        common_nouns = common_nouns[::-1]
                        common_nouns = " ".join(common_nouns)
                        attributes.append(common_nouns)
            if not objfound  :
              for child1 in token.children:
                 
                 if child1.dep_ == "prep":
                   
                    for child in child1.children:
                      if child.dep_ == "pobj":
                        
                        if child.lemma_ in nouns_in_files:
                        
                         nouns_in_text=[child.text]
                         for child1 in child.children:
                          if child1.dep_ in ("compound", "amod"):

                               for class_info in classes:

                                   if class_info["classname"] == child1.text:
                                       is_this_class=True
                                       subject=class_info["classname"]

                               nouns_in_text.append(convert_word_to_singular(child1))
                         common_nouns = sorted(nouns_in_text, key=lambda x: sentence[token.i].i)
                         common_nouns = common_nouns[::-1]
                         common_nouns = " ".join(common_nouns)
                         attributes.append(common_nouns)
                        
                        
                        for child in child1.children:
                         
                         if child.dep_ == "pobj": 
                          for child in child.children:
                          
                           if child.dep_ == "acl": 
                            for child1 in child.children:
                               
                                if child1.lemma_ in nouns_in_files:
                                 
                                  nouns_in_text=[child1.text]
                                  
                                  for child1 in child1.children:
                                     if child1.dep_ in ("compound", "amod"):
                                      
                                      for class_info in classes:

                                        if class_info["classname"] == child1.text:
                                         is_this_class=True
                                         subject=class_info["classname"]
                                     
                                      nouns_in_text.append(convert_word_to_singular(child1))
                                     
                            common_nouns = sorted(nouns_in_text, key=lambda x: sentence[token.i].i)
                            common_nouns = common_nouns[::-1]
                            common_nouns = " ".join(common_nouns)
                            attributes.append(common_nouns)
                                  
                                  
                                  
                                  
                                  
                      if child.dep_ == "pcomp" or (child.dep_ == "advcl" and child.tag_ == "VBG") or (child.dep_ == "acl" and child.tag_ == "VBG"):  
                        
                         for child in child.children:
                                if child.dep_ == "dobj":
                                 
                                 if child.lemma_ in nouns_in_files:
                                     nouns_in_text=[child.text]
                                     for child1 in child.children:
                                         if child1.dep_ in ("compound", "amod"):
                                                for class_info in classes:

                                                    if class_info["classname"] == child1.text:
                                                        is_this_class=True
                                                        subject=class_info["classname"]
                                                nouns_in_text.append(convert_word_to_singular(child1))
                                     common_nouns = sorted(nouns_in_text, key=lambda x: sentence[token.i].i)
                                     common_nouns = common_nouns[::-1]
                                     common_nouns = " ".join(common_nouns)
                                     attributes.append(common_nouns)
                                     
                                     
        if token.dep_ == "ROOT":
            for child in token.children:
                if child.dep_ == "dobj":
                    for child2 in child.children:
                        if child2.dep_ in ("compound", "amod"):
                           new_subject=child2.text +" "+ convert_word_to_singular(child)
                        if child2.dep_ in ("relcl"):
                            for child3 in child2.children:
                                if child3.dep_ == "dobj":
                                    subject=new_subject
                                    if child3.lemma_ in nouns_in_files:
                                        nouns_in_text=[child3.text]
                                        for child1 in child3.children:
                                         if child1.dep_ in ("compound", "amod"):
                                            for class_info in classes:
                                                if class_info["classname"] == child1.text:
                                                    is_this_class=True
                                                    subject=class_info["classname"]
                                        
                                            nouns_in_text.append(convert_word_to_singular(child1))
                                        common_nouns = sorted(nouns_in_text, key=lambda x: sentence[token.i].i)
                                        common_nouns = common_nouns[::-1]
                                        common_nouns = " ".join(common_nouns)
                                        attributes.append(common_nouns)           
                        
                         
                      
                        if child2.dep_ in ("prep"):
                           for child3 in child2.children:
                            if child3.dep_ in ("pcomp"):
                             for child4 in child3.children:
                                if child4.dep_ == "dobj":
                                    subject=new_subject
                                    if child4.lemma_ in nouns_in_files:
                                            nouns_in_text=[child4.text]
                                            for child1 in child4.children:
                                             if child1.dep_ in ("compound", "amod"):
                                    
                                                for class_info in classes:
                                                    if class_info["classname"] == child1.text:
                                                        is_this_class=True
                                                        subject=class_info["classname"]
                                            
                                                nouns_in_text.append(convert_word_to_singular(child1))
                                            common_nouns = sorted(nouns_in_text, key=lambda x: sentence[token.i].i)
                                            common_nouns = common_nouns[::-1]
                                            common_nouns = " ".join(common_nouns)
                                            attributes.append(common_nouns) 
                                    
                                    for child3 in child4.children:
                                        if child3.dep_ == "prep":
                                         for child in child3.children:
                                                if child.dep_ == "pobj":
                                                 if child.lemma_ in nouns_in_files:
                                                    nouns_in_text=[child.text]
                                                    for child1 in child.children:
                                                     if child1.dep_ in ("compound", "amod"):
                                                        for class_info in classes:
                                                            if class_info["classname"] == child1.text:
                                                                is_this_class=True
                                                                subject=class_info["classname"]
                                                    
                                                        nouns_in_text.append(convert_word_to_singular(child1))
                                                    common_nouns = sorted(nouns_in_text, key=lambda x: sentence[token.i].i)
                                                    common_nouns = common_nouns[::-1]
                                                    common_nouns = " ".join(common_nouns)
                                                    attributes.append(common_nouns) 
                                
                                
                             
    return subject, attributes



classes=[]
def feature_extraction_subject_phrase(sentences):
    for doc in sentences:
        sentence = nlp(doc)
        subject1 = extract_subject_phrase(sentence)

        if subject1:
            # Check if the subject is already in classes
            isthisclass = False
            for item in classes:
                if item["classname"] == subject1:
                    isthisclass = True
                    break
            if not isthisclass:
                classes.append({"classname": subject1, "attributes": [], "methods": []})

# Extract methods (M-Rule 1)
isthisteseted=False

def feature_extraction_extract_object(sentences):
    for doc in sentences:
        sentence = nlp(doc)
        subject2, direct_object2 = extract_object(sentence,classes)
        if subject2 and direct_object2:
            # Check if the subject is already in classes
            class_found = False
            for class_info in classes:
                if class_info["classname"] == subject2:

                    class_found = True
                    break

            if class_found:
                # Ensure we are modifying the correct class_info object
                for i in direct_object2:
                    isthisclass = False
                    for item in classes:
                        if item["classname"] == i:
                            isthisclass = True
                            break
                    if not isthisclass:
                        class_info["attributes"].append(i)

            if not class_found:
                new_attributes = []
                for i in direct_object2:
                    isthisclass = False
                    for item in classes:
                        if item["classname"] == i:
                            isthisclass = True
                            break
                    if not isthisclass:
                        new_attributes.append(i)
                classes.append({
                    "classname": subject2,
                    "attributes": new_attributes,
                     "methods": []
                })
def feature_extraction_from_direct_object(sentences):
    for doc in sentences:
        sentence = nlp(doc)
        # Extract subjects_list from the direct objects of the current sentence
        subjects_list = extract_from_direct_object(sentence,)
        if len(subjects_list) > 0:
            for subject3 in subjects_list:
                isthisclass = False
                for item in classes:
                    if item["classname"] == subject3:
                        isthisclass = True
                        break
                if not isthisclass:
                    classes.append({"classname": subject3, "attributes": [], "methods": []})

def feature_extraction_from_from_Posses(sentences):
      for doc in sentences:
        sentence = nlp(doc)
        subject4, direct_object4 = extract_from_Posses(sentence)
        if subject4 and direct_object4:
            # Check if subject is already in classes list
            class_found = False
            for class_info in classes:
                if class_info["classname"] == subject4:
                    isthisclass = False
                    class_found = True
                    for item in classes:
                        if item["classname"] == direct_object4:
                            isthisclass = True
                            break
                    if not isthisclass:
                        class_info["attributes"].append(direct_object4)

            # If subject not found, add it as a new class
            if not class_found:
                isthisclass = False
                for item in classes:
                    if item["classname"] == class_info["attributes"]:
                        isthisclass = True
                if not isthisclass:
                    classes.append({
                        "classname": subject4,
                        "attributes": [direct_object4],
                        "methods": []
                    })
def feature_extraction_from__noun_phrases(sentences):
    for doc in sentences:
        sentence = nlp(doc)
        noun_phrases = extract_noun_phrases(sentence)
        # Process noun phrases according to the rule
        for first_noun, remaining_nouns in noun_phrases:
            class_found = False
            for class_info in classes:
                 remaining_noun_list = remaining_nouns.split()
                 for noun in remaining_noun_list:

                      if class_info["classname"] == noun:

                          class_found = True
                          break

            if not class_found:
                for class_info in classes:
                    if class_info["classname"] == first_noun:
                     class_info["attributes"].append(remaining_nouns)

def feature_extraction_from__hasa_relationship(sentences):

    for doc in sentences:

        sentence = nlp(doc)
        hasa_relationships, relec, thishasrelcl = extract_hasa_relationship(sentence)

        # Process HasA relationships according to the rule
        for subject, obj in hasa_relationships:
            class_found = False
           
            # Split obj into individual words
            obj_words = obj.split()

            # Flag to check if any word in obj is a class
            obj_is_class = any(c['classname'] == obj for c in classes) 

            for class_info in classes:
                if class_info["classname"] == subject:

                    if  any(class_info["classname"]== word for word in obj_words):
                      
                      class_info["attributes"].append(obj)

                    if not obj_is_class:
                        class_info["attributes"].append(obj)
                    else:
                        if thishasrelcl:
                            class_info["attributes"].append(obj + " " + relec)

                    class_found = True


            # If the subject is not found in classes, add it as a new class with obj as an attribute
            if not class_found:
                if not obj_is_class:
                    classes.append({
                        "classname": subject,
                        "attributes": [obj],
                        "methods": []
                    })

#"---------------------------------------------------------------------------------------------------------------------------------------------"

def is_action_verb(token):

    non_action_verbs = {"be", "have", "include", "contain", "belong", "consist"}
    # Check if the verb is NOT in the list of non-action verbs
    is_not_non_action = token.lemma_ not in non_action_verbs

    # Check if the verb has a direct object (dobj) or prepositional object (pobj)
    has_object = any(child.dep_ in ["dobj", "pobj"] for child in token.children)

    # Check if it's not an auxiliary or modal verb
    is_main_verb = token.dep_ not in ["aux", "auxpass"]

    # Treat it as an action verb only if it has an object, is a main verb, and is not in the non-action verbs list
    return token.pos_ == "VERB" and has_object and is_main_verb and is_not_non_action


def extract_action_methods(sentences):
  for doc in sentences:
    sentence = nlp(doc)
    for token in sentence:
        if is_action_verb(token):  # Check if the token is an action verb
            subject = None
            for child in token.children:
                 if child.dep_ == "nsubj":  # Check if the token is a nominal subject
                  subject_phrase = [convert_word_to_singular(child)]
                  subject=convert_word_to_singular(child)
                  for child1 in child.children:
                    if child1.dep_ in ("compound", "amod"):
                       subject_phrase.append(convert_word_to_singular(child1))


                  subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
                  subject = " ".join(subject_phrase[::-1])
                  break
            if subject:

                for class_info in classes:
                 if class_info["classname"] == subject:
                    class_info["methods"].append(convert_word_to_singular(token))

                    # Associate the verb (method) with the subject

#"-------------------------------------------------------------------------------------------------"
association_details = []
def extract_association_relationships(sentences):

    for doc in sentences:
     sentence = nlp(doc)
     subject_phrase=None
     subject = None
     obj = None
     verb = None
     preposition = None
     class_found = False
     preposition = None
     # Identify Subject, Verb, Preposition, and Object in the sentence
     for token in sentence:
        #preposition = None
        if token.dep_ == "nsubj":  # Check if the token is a nominal subject
                  subject_phrase = [convert_word_to_singular(token)]
                  subject=convert_word_to_singular(token)
                  for child1 in token.children:
                    if child1.dep_ in ("compound", "amod"):
                       subject_phrase.append(convert_word_to_singular(child1))
                  subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
                  subject = subject_phrase[::-1]
                  subject = " ".join(subject)


        elif token.dep_ == "ROOT":
            verb = token.text
            for child in token.children:
                objisclass=False
                if child.dep_ in("dobj" ,"attr") :
                    obj = convert_word_to_singular(child)
                    for child2 in child.children:
                        if child2.dep_ in ("compound", "amod"):
                             obj =child2.text+ " "+ convert_word_to_singular(child)
                    for class_info in classes:
                                if class_info["classname"] ==obj:
                                  objisclass=True
                                elif class_info["classname"] ==convert_word_to_singular(child):
                                  obj =convert_word_to_singular(child)
                                  objisclass=True
                                else:
                                  obj2=obj.split()
                                  for obj_words_info in obj2:
                                    if class_info["classname"] == obj_words_info:
                                      obj=obj_words_info
                                      objisclass=True
                                      break
                            
        
                    if not objisclass:
                        for child1 in child.children:
                            if child1.dep_ in ("prep"):
                                for child2 in child1.children:
                                    if child2.dep_ in ("pobj"):
                                      obj =(convert_word_to_singular(child2))
                                      for child3 in child2.children:
                                         if child3.dep_ in ("compound", "amod"):
                                             obj =child3.text+ " "+ convert_word_to_singular(child2)
                                      break
                   
                    
     if not obj:
        for token in sentence:
        #preposition = None
            if token.dep_ == "nsubj":  # Check if the token is a nominal subject
                    subject_phrase = [convert_word_to_singular(token)]
                    subject=convert_word_to_singular(token)
                    for child1 in token.children:
                        if child1.dep_ in ("compound", "amod"):
                            subject_phrase.append(convert_word_to_singular(child1))
                    subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
                    subject = subject_phrase[::-1]
                    subject = " ".join(subject)


            elif token.dep_ == "ROOT":               
               for child in token.children:
                   if child.dep_ in ("prep"):
                       for child1 in child.children:
                            if child1.dep_ in ("pcomp"):
                              for child2 in child1.children:    
                                   if child2.dep_ in ("dobj"):  
                                       obj=convert_word_to_singular(child2)
                                       for child3 in child2.children:
                                         if child3.dep_ in ("compound", "amod"):
                                             obj =child3.text+ " "+ convert_word_to_singular(child2)
            
     if not obj:
        for token in sentence:
                 if token.dep_ == "ROOT":               
                  for child in token.children:
                     if child.dep_ in ("prep"):
                        for child1 in child.children:
                            if child1.dep_ in ("pobj"):
                                obj=convert_word_to_singular(child1)
                                for child3 in child1.children:
                                         if child3.dep_ in ("compound", "amod"):
                                             obj =child3.text+ " "+ convert_word_to_singular(child1)
                            
     # If we find a subject, verb, and either direct object or prepositional object, form an association
     if subject and obj and verb:
        if preposition:  # If there is a preposition, include it in the association label
            association_label = f"{verb} {preposition}"
        else:  # If no preposition, just use the verb (e.g., "has")
            association_label = verb
    # Map the association if both subject and object classes are found with a preposition and verb
        for class_info in classes:
                      if class_info["classname"] == subject:
                         for class_info in classes:
                          obj2=obj.split()
                          if class_info["classname"] == obj:
                           class_found = True
                          else:
                           for obj_words_info in obj2:
                            if class_info["classname"] == obj_words_info:
                             obj=obj_words_info
                            
                             class_found = True
        if class_found:
          association_details.append({
            "class_1": subject,
            "association_label": association_label,
            "class_2": obj,
            "type"  : None
        })
          


def identify_relationships(sentences):
    AG_RULES = {
    "composition": [
        "comprise", "have", "include", "possess", "contain", 
        "consist of", "constitute", "embed", "incorporate", 
        "encompass", "entail", "hold", "composed of", 
        "make up", "own"
    ],
    "aggregation": [
        "is a part of", "are a part of", 
        "is associated with", "are associated with",
        "belongs to", "belong to",  # Added here
        "is connected to", "relates to",
        "forms part of", "is included in"
    ]
}

# Combine all phrases into a single list for quick search
    ALL_PHRASES = AG_RULES["composition"] + AG_RULES["aggregation"]
    relationships = []  # To store the results for all sentences

    for doc in sentences:
        sentence = nlp(doc)
        # Check for multi-word phrases in the original sentence
        phrase_found = None
        for phrase in ALL_PHRASES:
            # Using regex to find exact phrases
            if re.search(rf"\b{re.escape(phrase)}\b", doc, re.IGNORECASE):
                phrase_found = phrase
                break

        # Initialize variables
        subject = None
        obj = None
        verb = None
        relationship_type = "None"
        relationship = None 
        # Parse the sentence using SpaCy
       

        # Extract subject, verb, and object
        for token in sentence:
            if token.dep_ == "nsubj":  # Check if the token is a nominal subject
                  subject_phrase = [convert_word_to_singular(token)]
                  subject=convert_word_to_singular(token)
                  for child1 in token.children:
                    if child1.dep_ in ("compound", "amod"):
                       subject_phrase.append(convert_word_to_singular(child1))
                  subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
                  subject = subject_phrase[::-1]
                  subject = " ".join(subject)
                  

            elif token.dep_ == "ROOT":
                verb = token.text
                for child in token.children:
                    objisclass=False
                    if child.dep_ == "dobj":
                        for child2 in child.children:
                            if child2.dep_ in ("compound", "amod"):
                             obj =child2.text+ " "+ convert_word_to_singular(child)
                             for class_info in classes:
                                if class_info["classname"] ==obj:
                                  objisclass=True
                                elif class_info["classname"] ==convert_word_to_singular(child):
                                  obj =convert_word_to_singular(child)
                                  objisclass=True
                                else:
                                  obj2=obj.split()
                                  for obj_words_info in obj2:
                                    if class_info["classname"] == obj_words_info:
                                      obj=obj_words_info
                                      objisclass=True
                                      break
                        if not objisclass:
                         for child1 in child.children:
                            if child1.dep_ in ("prep"):
                                for child2 in child1.children:
                                    if child2.dep_ in ("pobj"):
                                      obj = convert_word_to_singular(child2)
                                      for child3 in child2.children:
                                          if child3.dep_ in ("compound", "amod"):
                                            obj =child3.text+ " "+ convert_word_to_singular(child2)
                                      break
                              
        if not obj:
            
          for token in sentence:
        #preposition = None
            if token.dep_ == "nsubj":  # Check if the token is a nominal subject
                    subject_phrase = [convert_word_to_singular(token)]
                    subject=convert_word_to_singular(token)
                    for child1 in token.children:
                        if child1.dep_ in ("compound", "amod"):
                            subject_phrase.append(convert_word_to_singular(child1))
                    subject_phrase = sorted(subject_phrase, key=lambda x: sentence[token.i].i)
                    subject = subject_phrase[::-1]
                    subject = " ".join(subject)


            elif token.dep_ == "ROOT":               
                for child in token.children:
                   if child.dep_ in ("prep"):
                        for child1 in child.children:
                            if child1.dep_ in ("pcomp"):
                              for child2 in child1.children:    
                                   if child2.dep_ in ("dobj"): 
                                       obj = convert_word_to_singular(child2) 
                                       for child3 in child2.children:
                                          if child3.dep_ in ("compound", "amod"):
                                            obj =child3.text+ " "+ convert_word_to_singular(child2)  
                                       break 
        if not obj:   
            for token in sentence:
              if token.dep_ == "ROOT":
                for child1 in token.children:                                 
                        if child1.dep_ in ("prep"):
                            for child2 in child1.children:
                              if child2.dep_ in ("pobj"):  
                                       obj=child2.text   
                                       for child3 in child2.children:
                                        if child3.dep_ in ("compound", "amod"):
                                            obj =child3.text+ " "+ convert_word_to_singular(child2)  
                   
        if subject and obj:
           
        # Determine the relationship based on multi-word phrases or verb
            if phrase_found  :
                if phrase_found in AG_RULES["composition"]:
                    relationship_type = "Composition"
                    relationship = {"class_1": obj, "association_label": phrase_found, "class_2": subject, "type": relationship_type}
                elif phrase_found in AG_RULES["aggregation"]:
                    relationship_type = "Weak Aggregation"
                    relationship = {"class_1": subject, "association_label": phrase_found, "class_2": obj, "type": relationship_type}
            elif verb in AG_RULES["composition"]:
                relationship_type = "Composition"
                relationship = {"class_1": obj, "association_label": verb, "class_2": subject, "type": relationship_type}
            elif verb in AG_RULES["aggregation"]:
                relationship_type = "Weak Aggregation"
                relationship = {"class_1": subject, "association_label": verb, "class_2": obj, "type": relationship_type}
            else:
                continue  # No relationship found for this sentence
           
        # Append the relationship to the list
        if relationship:
         association_details.append(relationship)
         
    # Return the relationships found as a list
    return association_details          
          
          
def remove_generic_terms_from_classes(classes):
    # List of generic terms that should not be treated as classes
    # List of generic terms that should not be treated as classes
     generic_terms = {"attribute", "propertie", "feature", "detail"}

     def contains_generic_term(class_name):
        # Split the class name into parts and check each part
        class_parts = class_name.lower().split()
        return any(part in generic_terms for part in class_parts)

    # Filter out classes with generic terms in their names
     classes[:] = [cls for cls in classes if not contains_generic_term(cls["classname"])]
     print(classes)
          
def process_sentences_generic(sentences, classes):
    current_class = None  # Track the current active class
    generic_terms = ["attributes", "properties", "features", "items", "details"]  # Generic object terms

    # Define a generalized pattern where the determiner is optional
    base_class_pattern = rf"^(?:Each|The|A|An)?\s*(\w+)\s+\w+\s+(?:{('|'.join(generic_terms))})\.$"
    attribute_pattern = (
    r"^(?:The|Each|A|An|These|Those|This|That)?\s*"
    r"(?:attributes|properties|features|items|details)\s+"
    r"(?:have|has|include|possess|contain)\s+([\w\s,]+)\.$"
    )
    base_class_pattern2 = rf"^(?:Each|The|A|An)?\s*(\w+)\s+(?:\w+\s+)*\w+\s+(?:{'|'.join(generic_terms)})\.$"
    base_class_pattern3 = rf"^(?:Each|The|A|An)?\s*(\w+)\s+\w+\s+(?:\w+\s+)*\b(?:{'|'.join(generic_terms)})\b(?:\s+\w+)*\.$"
    for sentence in sentences:
        
        # Match a sentence defining a base class
        class_match = re.match(base_class_pattern, sentence)
        if not class_match:
            class_match = re.match(base_class_pattern2, sentence)
        if not class_match:
            class_match = re.match(base_class_pattern3, sentence)
            print(sentence)
            print(class_match)
        if class_match:
            current_class = class_match.group(1).strip()  # Extract the base class (e.g., "Book")
      
            # Check if the base class already exists
            class_exists = next((cls for cls in classes if cls["classname"] == current_class), None)
            if not class_exists:
                # Add the new class to the list
                classes.append({
                    "classname": current_class,
                    "attributes": [],
                    "methods": []
                })
            
        # Match a sentence listing attributes
        attribute_match = re.match(attribute_pattern, sentence)
       
        if attribute_match and current_class:
            attributes = [attr.strip() for attr in attribute_match.group(1).split(",")]  # Extract attributes
           
            # Add attributes to the current class
            class_exists = next((cls for cls in classes if cls["classname"] == current_class), None)
            if class_exists:
                for attr in attributes:
                    if attr not in class_exists["attributes"]:
                        for class_info in classes:
                          if class_info["classname"] == current_class:
                                class_info["attributes"].append(attr)
            else:
                # Handle cases where the class is unexpectedly missing
                print(f"Warning: No class found for attributes in sentence: '{sentence}'")

    # Reset the current class after processing all sentences
    current_class = None   
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          

def extract_from_pattern2(sentences):
    pattern = r"^(?:A|The|An)\s+(.*?)\sidentifies\s(?:a|the|an|these|those)?\s*([\w\s]+)(?:s)?\."

    for sentence in sentences:
        match = re.search(pattern, sentence)

        doc1 = nlp(sentence)

        if match:

            subject_phrase = []
            object = None

            # Process the matched sentence with SpaCy

            for token in doc1:
                if token.dep_ == "nsubj":  # Check for nominal subject
                    subject_phrase = [convert_word_to_singular(token)]
                    for child in token.children:
                        if child.dep_ in ("compound", "amod"):
                            subject_phrase.append(convert_word_to_singular(child))

                    # Sorting the subject phrase
                    subject_phrase = sorted(subject_phrase, key=lambda x: token.i)

                    subject_phrase = subject_phrase[::-1]  # Reverse to maintain order
                    object = " ".join(subject_phrase)  # Store as a string

            # Check for the root and direct object
                elif token.dep_ == "ROOT":
                    for child in token.children:
                        if child.dep_ == "dobj":

                            subject = convert_word_to_singular(child)
                            for child1 in child.children:
                                if child1.dep_ in ("compound", "amod"):
                                    object1 = convert_word_to_singular(child1)
                                    subject = object1+ " " + subject


            if object:
             
              is_this_class = any(item["classname"] == object for item in classes)
              if not is_this_class:
                is_this_class_exist = any(item["classname"] == subject for item in classes)
                if not is_this_class_exist:
                    # If the class does not exist, add a new class with the subject and its attributes
                    classes.append({
                        "classname": subject,
                        "attributes": [object],
                        "methods": []
                        
                    })
                else:
                    # If the class exists, append the object as an attribute to the existing class
                    for item in classes:
                        if item["classname"] == subject:
                            item["attributes"].append(object)
                            break

def extract_from_pattern3(sentences):
   pattern = r"(?:\w+(?:\s+\w+)*)?\s+(?:is|are)\s+(?:\w+\s+)?identified\s+by\s+(.*)"
   for sentence in sentences:
        match = re.search(pattern, sentence)

        doc1 = nlp(sentence)

        if match:
       
            subject_phrase = []
            object2 = None
            for token in doc1:
                if token.dep_ == "nsubjpass":  # Check for nominal subject
                    subject_phrase = [convert_word_to_singular(token)]
                    for child in token.children:
                        if child.dep_ in ("compound", "amod"):
                            subject_phrase.append(convert_word_to_singular(child))

                    # Sorting the subject phrase
                    subject_phrase = sorted(subject_phrase, key=lambda x: token.i)

                    subject_phrase = subject_phrase[::-1]  # Reverse to maintain order
                    subject = " ".join(subject_phrase)

                elif token.dep_ == "ROOT":
                    for child in token.children:
                        if child.dep_ == "agent":
                                    for child2 in child.children:
                                       if child2.dep_ == "pobj":
                                          object2 = convert_word_to_singular(child2)
                                          for child3 in child2.children:
                                             if child3.dep_ in ("compound", "amod"):
                                                compound_part = convert_word_to_singular(child3)
                                                object2 = compound_part+ " " + object2

            if object2:

              is_this_class = any(item["classname"] == object for item in classes)
              if not is_this_class:
                is_this_class_exist = any(item["classname"] == subject for item in classes)
                if not is_this_class_exist:
                    # If the class does not exist, add a new class with the subject and its attributes
                    classes.append({
                        "classname": subject,
                        "attributes": [object2],
                        "methods": []
                    })
                else:
                    # If the class exists, append the object as an attribute to the existing class
                    for item in classes:
                        if item["classname"] == subject:
                            item["attributes"].append(object2)
                            break


# Split the paragraph into individual sentences
startsentences = [sent.text for sent in nlp(paragraph).sents]
matched_sentences_pattern2=[]
matched_sentences_pattern3=[]

sentences2, matched_sentences_pattern3 = pattern3.process_sentences(startsentences)
sentences2, matched_sentences_pattern2= pattern2.extract_classes_and_attributes(sentences2)
feature_extraction_subject_phrase(sentences2)
feature_extraction_from_direct_object(sentences2)
extract_from_pattern2(matched_sentences_pattern2)
extract_from_pattern3(matched_sentences_pattern3)
#feature_extraction_subject_phrase(sentences2)

#feature_extraction_from_direct_object(sentences2)
feature_extraction_extract_object(sentences2)
feature_extraction_from__hasa_relationship (sentences2)


if isthisteseted:
 feature_extraction_from_from_Posses(sentences2)

remove_generic_terms_from_classes(classes)
process_sentences_generic(sentences2 , classes )
extract_action_methods(sentences2)




extract_association_relationships(sentences2)
identify_relationships(sentences2)
# for sentence in sentences2:
#   print(sentence)






def generate_class_diagram(classes, associations):
    uml_code = "@startuml\n"

    # Iterate through the classes and define them in PlantUML format
    for class_info in classes:
        classname = class_info['classname'].replace(" ", "_")
        uml_code += f"class {classname} {{\n"

        # Add attributes, replacing spaces with underscores
        unique_attributes = set()

        for attribute in class_info['attributes']:
            attribute = attribute.replace(" ", "_")
            unique_attributes.add(attribute)

        # Write unique attributes to the UML code
        for attribute in unique_attributes:
            uml_code += f"  {attribute}\n"

        # Add methods, replacing spaces with underscores in method names
        unique_methods = set()
        for method in class_info['methods']:
            method = method.replace(" ", "_")
            unique_methods.add(method)

        for method in unique_methods:
            uml_code += f"  {method}()\n"

        uml_code += "}\n\n"

    # To track the relationships between class pairs with priority to typed relationships
    seen_relationships = {}

    # Add associations between classes with relationship types
    for association in associations:
        class_1 = association["class_1"].replace(" ", "_")
        class_2 = association["class_2"].replace(" ", "_")
        association_label = association["association_label"].replace(" ", "_")
        relationship_type = association.get("type", None)

        # Determine the appropriate connector based on the relationship type
        if association_label == "is":
            # Generalization relationship (inheritance)
            connector = "<|--"
        elif relationship_type == "Weak Aggregation":
            connector = "o--"
        elif relationship_type == "Composition":
            connector = "*--"
        else:
            connector = "--"

        # Create a tuple for the class pair (ignoring order)
        class_pair = tuple(sorted([class_1, class_2]))

        # Add or update the relationship with priority to typed relationships
        if class_pair not in seen_relationships or (relationship_type and seen_relationships[class_pair] is None):
            seen_relationships[class_pair] = relationship_type
            uml_code += f"{class_1} {connector} {class_2} : {association_label}\n"

    uml_code += "@enduml"

    print(uml_code)


   

generate_class_diagram(classes, association_details)