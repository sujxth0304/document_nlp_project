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
import pandas as pd

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

# Function to extract skills from text (simple keyword-based approach)
def extract_skills(text):
    # Define a list of skills (this can be extended or customized)
    skills = ['python', 'java', 'machine learning', 'data analysis', 'deep learning', 'sql', 'nlp']
    text = preprocess_text(text)
    return [skill for skill in skills if skill in text]

# Load uploaded resumes
def load_uploaded_resumes(uploaded_files):
    resumes = {}
    for file in uploaded_files:
        if file.name.endswith(".docx"):
            resumes[file.name] = read_docx(file)
    return resumes

# Simple relevance scoring function
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
    st.set_page_config(page_title="DOCU-MATE QnA")
    st.header("DOCU-MATE QnA")

    # File upload UI
    uploaded_files = st.file_uploader("Upload your files", type=['docx'], accept_multiple_files=True)

    # Load uploaded resumes
    if uploaded_files:
        resumes = load_uploaded_resumes(uploaded_files)

        # Display uploaded resumes
        if resumes:
            st.subheader("Uploaded Files:")
            for filename, content in resumes.items():
                st.write(f"**{filename}**")
                st.write(content)
        else:
            st.write("No files uploaded yet.")

        # Job description input
        job_description = st.text_area("Enter a description")

        # Calculate relevance scores and recommend the best resume
        if job_description and resumes:
            relevance_scores = calculate_relevance_scores(job_description, resumes)
            
            if np.all(relevance_scores == 0):
                st.write("No relevant files.")
            else:
                # Determine the highest relevance score
                highest_score = np.max(relevance_scores)
                
                # Set a threshold based on the highest score (e.g., 70% of the highest score)
                threshold = 0.7 * highest_score

                # Extract skills from the job description
                job_skills = extract_skills(job_description)

                # Rank resumes based on scores
                sorted_resumes = sorted(zip(relevance_scores, resumes.keys()), reverse=True)
                
                # Create a DataFrame to store results
                results = []
                for score, filename in sorted_resumes:
                    match_status = 'Match' if score >= threshold else 'No Match'
                    # Check if resume mentions at least one skill from the job description
                    resume_skills = extract_skills(resumes[filename])
                    if match_status == 'No Match' and any(skill in job_skills for skill in resume_skills):
                        match_status = 'Partial Match'
                    results.append({'Resume': filename, 'Score': score, 'Match Status': match_status})

                results_df = pd.DataFrame(results)

                # Define a function for conditional formatting
                def color_match(val):
                    color = '#A1DE93' if val == 'Match' else '#70A1D7' if val == 'Partial Match' else '#F47C7C'
                    return f'background-color: {color}'

                # Apply the conditional formatting
                styled_df = results_df.style.applymap(color_match, subset=['Match Status'])

                # Display the results
                st.subheader('Matching Results')
                st.dataframe(styled_df, width = 1000)

if __name__ == "__main__":
    main()
