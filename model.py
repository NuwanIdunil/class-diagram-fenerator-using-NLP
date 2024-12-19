import tkinter as tk
from tkinter import scrolledtext
import os

import google.generativeai as genai
import Linguistic_analysis
import pattern3
from relcl import split_sentences_with_relcl
from sentpattern import filter_and_split_sentences
from sentpattern1 import filter_and_split_sentences1
from sentpattern2 import filter_and_split_sentences2
#AIzaSyAjFu01t2CwL5A3LHbK3-D-wZntxsyCwZQ
# Configure the Google Generative AI API
genai.configure(api_key="AIzaSyAbmFdSTN-7t-44XXCNk4cnxibnaJpIs54")

# Define the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config
)

chat_session = model.start_chat(
  history=[
  ]
)
# Function to handle paragraph processing
def process_paragraph():
    # Retrieve the input paragraph
    input_paragraph = input_text.get("1.0", tk.END).strip()

    # API Call 1: Replace pronouns with actual nouns
    # patta = "Rewrite the paragraph with only replacing pronouns with actual nouns: " + input_paragraph
    # response = chat_session.send_message(patta)
  
    # # API Call 2: Convert to simple present tense and split
    patta2 = (
        "Convert the following paragraph into simple present tense active voice with replacing pronouns, "
        "then split into sentences. Split sentences further if there is more than one object, "
        "noun, or subject.Specially output should not invcludes pronouns . Give me only the modified paragraph: " + input_paragraph
    )
    response = chat_session.send_message(patta2)
    print(response)
    # Process the modified paragraph
    modified_paragraph = response.text
    
    filtered_text = Linguistic_analysis.remove_adverbs(modified_paragraph)
    filtered_text = Linguistic_analysis.clean_sentences1(filtered_text)
    sentences = Linguistic_analysis.custom_sent_tokenize(filtered_text)
    modified_sentences=Linguistic_analysis.clean_sentences(sentences)
#modified_sentences=split_sentences_with_such_as(modified_sentences)
    modified_sentences=split_sentences_with_relcl(modified_sentences)

    modified_sentences=filter_and_split_sentences(modified_sentences)
    modified_sentences=filter_and_split_sentences1(modified_sentences)
    modified_sentences=Linguistic_analysis.clean_sentences(modified_sentences)

    modified_sentences=filter_and_split_sentences2(modified_sentences)
# print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

# # # #Apply the split_sentence_by_conjunction function
    result = Linguistic_analysis.process_sentences(modified_sentences)
    modified_sentences=Linguistic_analysis.split_sentence_by_multiple_subject(result)
    modified_sentences = Linguistic_analysis.split_sentence_by_conjunction(modified_sentences)

    modified_sentences = Linguistic_analysis.split_sentence_by_multiple_objects_pre(modified_sentences)
    modified_sentences = Linguistic_analysis.split_sentence_by_multiple_objects(modified_sentences)
    modified_sentences = Linguistic_analysis.split_sentence_by_conjunction(modified_sentences)
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    # sentences = Linguistic_analysis.custom_sent_tokenize(modified_paragraph)
    # result = Linguistic_analysis.process_sentences(sentences)
    # modified_sentences= Linguistic_analysis.filter_and_split_sentences(result)
    # modified_sentences= Linguistic_analysis.filter_and_split_sentences1(modified_sentences)
    # modified_sentences= Linguistic_analysis.filter_and_split_sentences2(modified_sentences)
    # modified_sentences =  Linguistic_analysis.split_sentence_by_conjunction(modified_sentences)
    # modified_sentences =  Linguistic_analysis.process_sentences(modified_sentences)
    # modified_sentences =  Linguistic_analysis.split_sentence_by_multiple_objects_pre(modified_sentences)
    # modified_sentences =  Linguistic_analysis.split_sentence_by_multiple_objects(modified_sentences)
    
    # Display the processed output
    output_text.delete("1.0", tk.END)  # Clear previous output
    for sentence in modified_sentences:
        output_text.insert(tk.END, sentence + "\n")

# Setting up the Tkinter window
root = tk.Tk()
root.title("Paragraph Processing for Class Diagram Generation")
root.geometry("800x600")

# Input Label
input_label = tk.Label(root, text="Input Paragraph:")
input_label.pack(pady=10)

# Input Text Box
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
input_text.pack(pady=5)

# Process Button
process_button = tk.Button(root, text="Process Paragraph", command=process_paragraph)
process_button.pack(pady=20)

# Output Label
output_label = tk.Label(root, text="Processed Output:")
output_label.pack(pady=10)

# Output Text Box
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=15)
output_text.pack(pady=5)

# Start the Tkinter main loop
root.mainloop()
