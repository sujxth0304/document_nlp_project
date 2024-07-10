import streamlit as st
import spacy
from spacy import displacy
import docx2txt
import PyPDF2
from io import StringIO
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# Load the spaCy model
nlp = spacy.load("en_core_web_md")

# Function to display entities
def show_ents(doc):
    ents = []
    if doc.ents:
        for ent in doc.ents:
            ents.append({
                "text": ent.text,
                "label": ent.label_,
                "explanation": spacy.explain(ent.label_)
            })
    return ents

# Function to extract text from a PDF
# Function to extract text from a PDF
def extract_text_from_pdf(pdf):
    pdf_reader = PyPDF2.PdfReader(pdf)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

# Function to extract text from a Word document
def extract_text_from_docx(docx):
    return docx2txt.process(docx)

# Main function for the NER application
def main():
    st.title("Named Entity Recognition")

    # Text input section
    st.header("NER on Text")
    text = st.text_area("Enter text to analyze:", "When Sujith Santhosh started working on machine learning at Google in 2025, few people outside of the company took him seriously.")

    if st.button("Analyze Text"):
        doc = nlp(text)
        html = displacy.render(doc, style='ent', jupyter=False, options={"compact": True})
        st.markdown(html, unsafe_allow_html=True)
        ents = show_ents(doc)
        if ents:
            st.subheader("Detected Entities")
            for ent in ents:
                st.write(f"**{ent['text']}** - {ent['label']} - {ent['explanation']}")
        else:
            st.write("No entities found")

    # Document input section
    st.header("NER on Documents")
    uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx"])

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(uploaded_file)
        
        doc = nlp(text)
        html = displacy.render(doc, style='ent', jupyter=False, options={"compact": True})
        st.markdown(html, unsafe_allow_html=True)
        ents = show_ents(doc)
        if ents:
            st.subheader("Detected Entities")
            for ent in ents:
                st.write(f"**{ent['text']}** - {ent['label']} - {ent['explanation']}")
        else:
            st.write("No entities found")

if __name__ == "__main__":
    main()
