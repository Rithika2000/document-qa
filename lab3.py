import streamlit as st
from openai import OpenAI

st.title("My Lab3 Question Answering Chatbot")

# Sidebar for model selection and buffer size
openAI_model = st.sidebar.selectbox("Which Model?", ("mini", "regular"))
buffer_size = st.sidebar.slider("Buffer Size", min_value=1, max_value=10, value=2, step=1)

# Select the model to use based on the selection
if openAI_model == "mini":
    model_to_use = "gpt-4o-mini"
else:
    model_to_use = "gpt-4o"

# Initialize the OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OpenAI_key"]
    st.session_state.client = OpenAI(api_key=api_key)

# Initialize the conversation buffer and state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "awaiting_more_info" not in st.session_state:
    st.session_state["awaiting_more_info"] = False

# Display chat messages
for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

# Handle user input
if prompt := st.chat_input("Type your question here..."):
    if st.session_state.awaiting_more_info:
        if prompt.lower() == "yes":
            st.session_state.messages.append({"role": "user", "content": "Please provide more information."})
            # Generate the additional response from the model
            client = st.session_state.client
            stream = client.chat.completions.create(
                model=model_to_use,
                messages=st.session_state.messages,
                stream=True
            )
            additional_info = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": additional_info})
            st.session_state.messages.append({"role": "assistant", "content": "DO YOU WANT MORE INFO?"})
        elif prompt.lower() == "no":
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": "What else can I help you with?"})
        st.session_state.awaiting_more_info = False
    else:
        # Add user message to the buffer
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Limit the buffer to the specified size
        if len(st.session_state.messages) > buffer_size * 2:
            st.session_state.messages = st.session_state.messages[-buffer_size * 2:]

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate the response from the model
        client = st.session_state.client
        stream = client.chat.completions.create(
            model=model_to_use,
            messages=st.session_state.messages,
            stream=True
        )

        # Process the assistant response
        response = st.write_stream(stream)

        # Add assistant response to the buffer
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Ask if the user wants more info
        st.session_state.messages.append({"role": "assistant", "content": "DO YOU WANT MORE INFO?"})
        with st.chat_message("assistant"):
            st.markdown(f"{response} <br> DO YOU WANT MORE INFO?")

        st.session_state.awaiting_more_info = True
