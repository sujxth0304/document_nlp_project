import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from transformers import pipeline
import nltk
from nltk.corpus import words as nltk_words
from spellchecker import SpellChecker
from nltk.tokenize import sent_tokenize, word_tokenize
import os

# Download NLTK resources (if not already downloaded)
nltk_data_path = os.path.join(os.getenv('APPDATA'), 'nltk_data')

if not os.path.exists(nltk_data_path):
    nltk.download('punkt')
    nltk.download('words')
else:
    nltk.data.path.append(nltk_data_path)

def sentences_to_words_list(file_path):
    try:
        # Read the entire file
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Tokenize into sentences
        sentences = sent_tokenize(text)

        # Tokenize each sentence into words and store in a list
        words_list = []
        for sentence in sentences:
            words = word_tokenize(sentence)
            words_list.extend(words)

        return words_list
    
    except Exception as e:
        print(f"Error reading or tokenizing file: {e}")
        return None
    
file_path = 'src/shakespeare.txt'  # Replace with your file path
words_list = sentences_to_words_list(file_path)

# Initialize the spell checker and text-generation pipeline for text correction
spell = SpellChecker()
corrector = pipeline("text2text-generation", "pszemraj/bart-base-grammar-synthesis")

def correct_text(text, chunk_size=600):
    corrected_text = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        corrected_chunk = corrector(chunk)[0]['generated_text']
        corrected_text.append(corrected_chunk)
    return ''.join(corrected_text)

def extract_text_from_file(file):
    try:
        if file.type == 'application/pdf':
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            return text
        elif file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            document = Document(file)
            text = ""
            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            return None  # Indicate unsupported format
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None
    
def underline_misspelled(text, words_list):
    words = text.split()
    english_words = set(nltk_words.words())
    underlined_text = []

    for word in words:
        # Check if the word is in NLTK English words or is misspelled
        if word.lower() in english_words or word.lower() in spell or word.lower() in words_list:
            underlined_text.append(word)
        else:
            underlined_text.append(f'<span style="color: red; text-decoration: underline;">{word}</span>')

    return ' '.join(underlined_text)

def main():
    st.markdown("<h1>Autocorrector 📄</h1>", unsafe_allow_html=True)
    st.markdown("<h4><i>It may take some time depending on the size of the document</i></h4>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload Files:", accept_multiple_files=True)
    
    # Initialize an empty words_list
    words_list = []

    # Process each uploaded file
    for uploaded_file in uploaded_files:
        st.write("filename:", uploaded_file.name)
        extracted_text = extract_text_from_file(uploaded_file)
        
        if extracted_text is not None:
            paragraphs = extracted_text.split('\n')
            corrected_paragraphs = []
            underlined_paragraphs = []
            my_bar = st.progress(0)  # Initialize progress bar
            total_paragraphs = len(paragraphs)

            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():  # Only process non-empty paragraphs
                    corrected_paragraph = correct_text(paragraph)
                    corrected_paragraphs.append(corrected_paragraph)
                    underlined_paragraph = underline_misspelled(paragraph, words_list)
                    underlined_paragraphs.append(underlined_paragraph)

                else:
                    corrected_paragraphs.append(paragraph)
                    underlined_paragraphs.append(paragraph)

                my_bar.progress((i + 1) / total_paragraphs)  # Update progress

            corrected_text = '\n'.join(corrected_paragraphs)
            underlined_text = '\n'.join(underlined_paragraphs)

            st.write("Corrected Text:")
            st.write(corrected_text)

            st.markdown("<h2>Text with underlined errors:</h2>", unsafe_allow_html=True)
            st.markdown(underlined_text, unsafe_allow_html=True)
            # Add a download button for the corrected text
            st.download_button(
                label="Download Corrected Text",
                data=corrected_text,
                file_name=f"corrected_{uploaded_file.name}.txt",
                mime="text/plain"
            )
        else:
            st.write("This file format is not currently supported for spell checking.")

if __name__ == "__main__":
    main()
