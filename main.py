import streamlit as st
from openai import OpenAI
import tiktoken

st.title("ChatGPT Streamlit App")

# Sidebar for user inputs
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
model = st.sidebar.selectbox("Choose a model", ["gpt-4o", "gpt-4o-mini"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to count tokens
def count_tokens(text, model):
    # Note: tiktoken might not have encodings for gpt-4o and gpt-4o-mini
    # We'll use gpt-4 encoding as an approximation
    encoding = tiktoken.encoding_for_model("gpt-4")
    return len(encoding.encode(text))

# Function to get completion from OpenAI
def get_completion(messages, model, temperature):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.chatanywhere.tech/v1"
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content, response.usage.total_tokens

# Chat input
if prompt := st.chat_input("What would you like to ask?"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            messages_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            response, total_tokens = get_completion(messages_for_api, model, temperature)
            message_placeholder.markdown(response)
            full_response = response

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Display token usage
        st.sidebar.write(f"Total tokens used in this response: {total_tokens}")

# Display current token count for the conversation
total_conversation_tokens = sum(count_tokens(m["content"], model) for m in st.session_state.messages)
st.sidebar.write(f"Total tokens in conversation: {total_conversation_tokens}")