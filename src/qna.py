import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Function to preprocess text
def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    preprocessed_text = ' '.join(words)
    return preprocessed_text

# Function to read text from DOCX file
def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Load uploaded resumes
def load_uploaded_resumes(uploaded_files):
    resumes = {}
    for file in uploaded_files:
        if file.name.endswith(".docx"):
            resumes[file.name] = read_docx(file)
    return resumes

# Simple relevance scoring function (example)
def calculate_relevance_scores(job_description, resumes):
    vectorizer = TfidfVectorizer(stop_words='english')
    corpus = [preprocess_text(job_description)] + [preprocess_text(resume) for resume in resumes.values()]
    X = vectorizer.fit_transform(corpus)
    job_vec = X[0]  # TF-IDF vector for job description
    resume_vecs = X[1:]  # TF-IDF vectors for resumes

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(job_vec, resume_vecs).flatten()
    return cosine_similarities

# Streamlit app
def main():
    st.set_page_config(page_title="Job Description to Resume Predictor")
    st.header("Job Description to Resume Predictor")

    # File upload UI
    uploaded_files = st.file_uploader("Upload your resumes", type=['docx'], accept_multiple_files=True)

    # Load uploaded resumes
    if uploaded_files:
        resumes = load_uploaded_resumes(uploaded_files)

        # Display uploaded resumes
        if resumes:
            st.subheader("Uploaded Resumes:")
            for filename, content in resumes.items():
                st.write(f"**{filename}**")
                st.write(content)
        else:
            st.write("No resumes uploaded yet.")

        # Job description input
        job_description = st.text_area("Enter job description")

        # Calculate relevance scores and recommend the best resume
        if job_description and resumes:
            relevance_scores = calculate_relevance_scores(job_description, resumes)
            
            if np.all(relevance_scores == 0):
                st.write("No relevant files.")
            else:
                # Rank resumes based on scores
                sorted_resumes = sorted(zip(relevance_scores, resumes.keys()), reverse=True)
                
                # Display ranked resumes
                st.subheader("Ranked Resumes:")
                for score, filename in sorted_resumes:
                    st.write(f"Resume: {filename}, Score: {score}")

if __name__ == "__main__":
    main()
