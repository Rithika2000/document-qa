import chromadb
from chromadb.utils import embedding_functions
import openai
from PyPDF2 import PdfReader
import os
import streamlit as st

# Function to construct the ChromaDB collection and add PDF files as documents
def create_chromadb_collection():
    # Initialize ChromaDB client
    client = chromadb.Client()

    # Create a new collection
    collection_name = "Lab4Collection"
    collection = client.create_collection(collection_name)

    # Ensure the OpenAI client is initialized
    if 'openai_client' not in st.session_state:
        api_key = st.secrets["OpenAI_key"]
        st.session_state.openai_client = openai
    
    # Function to read PDFs and convert to text
    def pdf_to_text(file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()  # Extract text from each page
        return text

    # Function to add a document to the collection
    def add_to_collection(collection, text, filename):
        openai_client = st.session_state.openai_client
        response = openai_client.Embedding.create(
            input=text,
            model='text-embedding-3-small'
        )
        embedding_vector = response['data'][0]['embedding']

        collection.add(
            documents=[text],
            ids=[filename],
            embeddings=[embedding_vector]
        )

    # Add PDF documents into the ChromaDB collection
    pdf_folder = "path_to_pdf_files"  # Replace with the path to your PDFs
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
    openai_client = st.session_state.openai_client
    response = openai_client.Embedding.create(
        input=topic,
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
query_collection(chromadb.Client().get_collection("Lab4Collection"), topic)
