import openai
import streamlit as st
import os
import chromadb
from PyPDF2 import PdfReader

# Initialize the OpenAI client
if 'openai_client' not in st.session_state:
    api_key = st.secrets["OpenAI_key"]
    openai.api_key = api_key
    st.session_state.openai_client = openai

client = chromadb.PersistentClient(path="/workspaces/document-qa/data")

# Function to construct the ChromaDB collection and add PDF files as documents
def create_chromadb_collection():
    collection_name = "Lab4Collection_2"
    collection = client.create_collection(collection_name)

    # Function to read PDFs and convert to text
    def pdf_to_text(file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    # Function to add a document to the collection
    def add_to_collection(collection, text, filename):
        response = st.session_state.openai_client.embeddings.create(
            input=[text],
            model='text-embedding-3-small'
        )
        embedding_vector = response['data'][0]['embedding']

        collection.add(
            documents=[text],
            ids=[filename],
            embeddings=[embedding_vector]
        )

    # Add PDF documents into the ChromaDB collection
    pdf_folder = "/workspaces/document-qa/data"  
    for file_name in os.listdir(pdf_folder):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, file_name)
            text_content = pdf_to_text(file_path)
            add_to_collection(collection, text_content, file_name)

    print(f"Documents added to ChromaDB collection '{collection_name}'.")

# Sidebar for topic selection
topic = st.sidebar.selectbox("Topic", ("Text Mining", "GenAI"))

# Function to query the collection
def query_collection(collection, topic):
    response = st.session_state.openai_client.embeddings.create(
        input=[topic],
        model="text-embedding-3-small"
    )
    query_embedding = response['data'][0]['embedding']

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        st.write(f"The following file/syllabus might be helpful: {doc_id}")

# Example usage
create_chromadb_collection()

# After creating the collection, you can query it using the selected topic
query_collection(client.get_collection("Lab4Collection"), topic)
