import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_pdf_text(pdf):
    text = ""
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_word_text(docx):
    text = ""
    doc = Document(docx)
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in the provided context just say "answer is not available in the context", don't provide the wrong answer \n\n
    Context:\n{context}?\n
    Question:\n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.6)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Ensure the FAISS index file exists
    if not os.path.exists("faiss_index/index.faiss"):
        st.error("FAISS index file not found. Please process the documents first.")
        return

    # Set allow_dangerous_deserialization to True
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True)
    print(response)
    st.write("Reply: ", response["output_text"])

def main():
    st.set_page_config(page_title="Chat with Document")
    st.header("Chat with Docs")

    user_question = st.text_input("Ask a question from the doc files")

    if user_question:
        user_input(user_question)
    with st.sidebar:
        st.title("Menu:")
        uploaded_files = st.file_uploader("Upload your PDF or Word files and click on the submit button", accept_multiple_files=True, type=['pdf', 'docx'])
        if st.button("Submit & Process"):
            if uploaded_files:
                with st.spinner("Processing..."):
                    raw_text = ""
                    for uploaded_file in uploaded_files:
                        if uploaded_file.name.endswith(".pdf"):
                            raw_text += get_pdf_text(uploaded_file)
                        elif uploaded_file.name.endswith(".docx"):
                            raw_text += get_word_text(uploaded_file)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("Done")
            else:
                st.error("Please upload PDF or Word files first.")

if __name__ == "__main__":
    main()
