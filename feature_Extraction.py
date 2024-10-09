import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")
classes = []

# Paragraph to be split into sentences and analyzed
paragraph = """
The library identifies each book by a title.
The library identifies each book by a an author.
The library identifies each book by a an ISBN number.
Each book has a title.
Each book has a an author.
Each book has a.
Each book has a an ISBN number .
Registered patrons are members.
Members have names.
Members have unique membership IDs.
Members borrow books from the library.
Each transaction is recorded for accountability.
The transaction notes the borrowing date.
The transaction notes the return date.
Staff members oversee library type.
Staff members have names.
Staff members have employee IDs.
Staff members manage the library's collection of books.
The collection of books is organized into different sections.
The sections are located throughout the library premises.
"""

# Function to extract subject phrases from a sentence
def extract_subject_phrase(sentence):
    for token in sentence:
        if token.dep_ == "nsubj":  # Check if the token is a nominal subject
            subject_phrase = [token]
            for child in token.children:
                if child.dep_ in ("compound", "amod"):
                    subject_phrase.append(child)
            subject_phrase = sorted(subject_phrase, key=lambda x: x.i)
            return " ".join([t.text for t in subject_phrase])
    return ""

# Function to extract direct objects from a sentence
def extract_from_Posses(sentence):
    subject = None
    direct_object = None

    for token in sentence:
        if token.dep_ == "nsubj":  # Check if the token is a nominal subject
            subject = token.text
        elif token.dep_ == 'poss':
            direct_object = token.head.text
            subject = token.text
          
    return subject, direct_object

def extract_from_direct_object(sentence):
    subjects = []
    for token in sentence:
        if token.dep_ == "nsubj" and token.head.dep_ == "ROOT":
            for child1 in token.head.children:
                if child1.dep_ == "dobj":
                    for child2 in child1.children:
                        if child2.pos_ == "VERB" and child2.dep_ != "pcomp":
                            for child3 in child2.children:
                                if child3.dep_ == "dobj":
                                    subjects.append(child3.text)
        elif token.dep_ == "ROOT":
            for child2 in token.children:
                if child2.dep_ == "prep":
                    for child3 in child2.children:
                        if child3.dep_ == "pobj":
                            subjects.append(child3.text)
                if child2.pos_ == "VERB" and child2.dep_ != "pcomp":
                    for child3 in child2.children:
                        if child3.dep_ == "dobj":
                            subjects.append(child3.text)
    return subjects

def extract_noun_phrases(sentence):
    noun_phrases = []
    for chunk in sentence.noun_chunks:
        nouns = [token for token in chunk if token.pos_ == "NOUN" or token.dep_ == "amod"]
        if len(nouns) >= 2:
            noun_phrases.append((nouns[0].text, " ".join(noun.text for noun in nouns[1:])))
    return noun_phrases

def extract_hasa_relationship(sentence):
    hasa_relationships = []
    for token in sentence:
        if token.lemma_ in ("have", "has"):
            subject = None
            obj = None
            for child in token.children:
                if child.dep_ == "nsubj":
                    subject = child.text
                elif child.dep_ in ("dobj", "attr"):
                    obj = child.text
                    additional_obj_parts = []
                    for child1 in child.children:
                        if child1.dep_ in ("amod", "compound"):
                            additional_obj_parts.append(child1.text)
                    if additional_obj_parts:
                        obj = " ".join(additional_obj_parts) + " " + obj
            if subject and obj:
                hasa_relationships.append((subject, obj))
    return hasa_relationships

def extract_object(sentence):
    def read_nouns_from_files(file_paths):
        nouns = set()
        for file_path in file_paths:
            with open(file_path, 'r') as file:
                nouns.update(line.strip() for line in file)
        return nouns
    
    file_paths = ['corpus_Int.txt', 'corpus_String.txt', 'corpus_Double.txt']
    nouns_in_text = []
    subject = ""
    
    nouns_in_files = read_nouns_from_files(file_paths)
    
    for token in sentence:
        if token.dep_ == "nsubj":  # Check if the token is a nominal subject
            subject_phrase = [token]
            for child in token.children:
                if child.dep_ in ("compound", "amod"):
                    subject_phrase.append(child)
            subject_phrase = sorted(subject_phrase, key=lambda x: x.i)
            subject = " ".join([t.text for t in subject_phrase])
        
        if token.dep_ == "ROOT": 
            for child in token.children:
                if child.dep_ == "dobj":
                    nouns_in_text.append(child.text)
                    for child1 in child.children:
                        nouns_in_text.append(child1.text)
    
    common_nouns = nouns_in_files.intersection(nouns_in_text)
    return subject, common_nouns

def feature_extraction(sentences):
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
                classes.append({"classname": subject1, "attributes": []})

        subject2, direct_object2 = extract_object(sentence)
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
                    "attributes": new_attributes
                })

        # Extract subjects_list from the direct objects of the current sentence
        subjects_list = extract_from_direct_object(sentence)
        if len(subjects_list) > 0:
            for subject3 in subjects_list:
                isthisclass = False
                for item in classes:
                    if item["classname"] == subject3:
                        isthisclass = True
                        break
                if not isthisclass:
                    classes.append({"classname": subject3, "attributes": []})

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
                        "attributes": [direct_object4]
                    })
                    
        noun_phrases = extract_noun_phrases(sentence)

        # Process noun phrases according to the rule
        for first_noun, remaining_nouns in noun_phrases:
            class_found = False
            for class_info in classes:
                if class_info["classname"] == first_noun:
                    class_info["attributes"].append(remaining_nouns)
                    class_found = True
                    break
        
        hasa_relationships = extract_hasa_relationship(sentence)
        # Process HasA relationships according to the rule
        for subject, obj in hasa_relationships:
            class_found = False
            for class_info in classes:
                if class_info["classname"] == subject:
                    # Check if obj is not already a class
                    if not any(c['classname'] == obj for c in classes):
                        class_info["attributes"].append(obj)
                    class_found = True
                    break

            # If the subject is not found in classes, add it as a new class with obj as attribute
            if not class_found:
                if not any(c['classname'] == obj for c in classes):
                    classes.append({
                        "classname": subject,
                        "attributes": [obj]
                    })
   
    return classes

# Split the paragraph into individual sentences
sentences = [sent.text for sent in nlp(paragraph).sents]
classes = feature_extraction(sentences)
print(classes)
