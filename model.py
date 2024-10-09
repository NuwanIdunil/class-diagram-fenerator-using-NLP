

import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyAjFu01t2CwL5A3LHbK3-D-wZntxsyCwZQ")

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
  ]
)
para=" Books are central, each identified by a title, author, and ISBN number. Members, who are registered patrons, have names and unique membership IDs. They have the ability to borrow books from the library, with each transaction recorded for accountability, noting the borrowing and return dates. Staff members, who oversee library operations, are identified by their names and employee IDs. They manage the library's collection of books, which are organized into different sections located throughout the library premises." 
patta="replace pro nouns with actual noun ,after that convert following paragraph into simple present tence active voice.,then split into sentences, then again splitting it into different sentences if there is more than one object or noun or subject.give me only answer paragraph.no need explanation " + para
response = chat_session.send_message(patta)

print(response.text)

import Linguistic_analysis

# Assuming 'response.text' contains the modified paragraph as a single string
modified_paragraph = response.text
sentences=Linguistic_analysis.custom_sent_tokenize(modified_paragraph)
result = Linguistic_analysis.process_sentences(sentences)
# modified_sentences = []
# Process sentences and split into individual sentences
#sentences = Linguistic_analysis.process_sentences(modified_paragraph)
modified_sentences = Linguistic_analysis.split_sentence_by_conjunction(sentences)
# modified_sentences = Linguistic_analysis.split_sentence_by_multiple_subject(modified_sentences)
modified_sentences = Linguistic_analysis.split_sentence_by_multiple_objects(modified_sentences)

# Print each modified sentence
for sentence in modified_sentences:            
     print(sentence)