import streamlit as st
from openai import OpenAI, OpenAIError

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below, and select a summary option – GPT will summarize it! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Validate the key as soon as it is entered.
openai_api_key = st.text_input("OpenAI API Key", type="password")

if openai_api_key:
    try:
        # Create an OpenAI client
        client = OpenAI(api_key=openai_api_key)
        client.models.list()
        st.success("API key is valid! You can proceed.", icon="✅")
    except OpenAIError as e:
        st.error("Invalid API key. Please check and try again.", icon="❌")
        st.stop()

if openai_api_key:

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

        # Generate an answer using the OpenAI API with the new model.
        stream = client.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
    except OpenAIError as e:
        st.error(f"An error occurred: {e}")
