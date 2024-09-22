import openai
import streamlit as st
import os

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from PyPDF2 import PdfReader

# Initialize the OpenAI client
if 'openai_client' not in st.session_state:
    api_key = st.secrets["OpenAI_key"]
    openai.api_key = api_key
    st.session_state.openai_client = openai

# Initialize the ChromaDB client
client = chromadb.PersistentClient(path="/workspaces/document-qa/data")

# Function to create ChromaDB collection and store in session state
def create_chromadb_collection():
    if 'Lab4_vectorDB' not in st.session_state:
        collection_name = "Lab4Collection"
        existing_collections = client.list_collections()
        
        if collection_name in [col.name for col in existing_collections]:
            collection = client.get_collection(collection_name)
        else:
            collection = client.create_collection(collection_name)

        def pdf_to_text(file_path):
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text

        def add_to_collection(collection, text, filename):
            response = st.session_state.openai_client.embeddings.create(
                input=[text],
                model='text-embedding-3-small'
            )
            embedding_vector = response.data[0].embedding

            collection.add(
                documents=[text],
                ids=[filename],
                embeddings=[embedding_vector],
                metadatas=[{'filename': filename}]
            )

        pdf_folder = "/workspaces/document-qa/data"
        for file_name in os.listdir(pdf_folder):
            if file_name.endswith(".pdf"):
                file_path = os.path.join(pdf_folder, file_name)
                text_content = pdf_to_text(file_path)
                add_to_collection(collection, text_content, file_name)

        st.session_state.Lab4_vectorDB = collection
        print(f"Collection '{collection_name}' is ready.")

# Function to query the collection and construct the prompt for the chatbot
def query_collection_and_chat(collection, user_input):
    response = st.session_state.openai_client.embeddings.create(
        input=[user_input],
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    relevant_texts = [result for result in results['documents'][0]]
    return relevant_texts

# Streamlit chat interface
st.title("Course Information Chatbot")

if 'messages' not in st.session_state:
    st.session_state.messages = []

create_chromadb_collection()

# Add a character limit for user input
user_input = st.text_input("Ask a question about the course:", max_chars=200)

if st.button("Send"):
    if user_input:
        relevant_texts = query_collection_and_chat(st.session_state.Lab4_vectorDB, user_input)

        # Limit to the first two relevant texts
        limited_texts = relevant_texts[:2]

        # Construct prompt for the LLM
        prompt = "Relevant excerpts:\n\n"
        prompt += "\n\n".join(limited_texts) + "\n\n"
        prompt += f"User question: {user_input}\nAnswer:"

        # Call the LLM
        response = st.session_state.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content

        # Store the conversation in session state
        st.session_state.messages.append({"user": user_input, "bot": answer})

# Display chat history
if st.session_state.messages:
    for message in st.session_state.messages:
        st.write(f"You: {message['user']}")
        st.write(f"Bot: {message['bot']}")
