import streamlit as st
from openai import OpenAI, OpenAIError

# Show title and description.
st.title("Lab 2 - Document Question Answering")
st.write(
    "Upload a document below, and select a summary option – GPT will summarize it! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Fetch the OpenAI API key from secrets
#openai_api_key = st.secrets["OpenAI_key"]

# Sidebar options for summary type
summary_type = st.sidebar.radio(
    "Choose a summary option:",
    (
        "Summarize the document in 100 words",
        "Summarize the document in 2 connecting paragraphs",
        "Summarize the document in 5 bullet points",
    )
)

# Sidebar option for choosing the model
use_advanced_model = st.sidebar.checkbox("Use Advanced Model (GPT-4o)")

# Model selection
model = "gpt-4o" if use_advanced_model else "gpt-4o-mini"

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)", type=("txt", "md")
)

# Only proceed if a file is uploaded
if uploaded_file:
    # Read and decode the uploaded file
    document = uploaded_file.read().decode()

    # Construct the summary prompt based on the selected summary type
    if summary_type == "Summarize the document in 100 words":
        instruction = "Please summarize the document in 100 words."
    elif summary_type == "Summarize the document in 2 connecting paragraphs":
        instruction = "Please summarize the document in 2 connecting paragraphs."
    else:
        instruction = "Please summarize the document in 5 bullet points."

    messages = [
        {
            "role": "user",
            "content": f"Here's a document: {document} \n\n---\n\n {instruction}",
        }
    ]

    # Generate an answer using the OpenAI API
    try:
        client = OpenAI(api_key=openai_api_key)  # Use the API key from secrets
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
    except OpenAIError as e:
        st.error(f"An error occurred: {e}")
