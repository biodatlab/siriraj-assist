import pickle
import json
import numpy as np
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


### Load the index and chunks

with open("faiss_index.pkl", "rb") as f:
    index = pickle.load(f)

with open("baby_0_3.json", "r", encoding="utf-8-sig") as f:
    chunks = json.load(f)

### OpenAI API
client = OpenAI()

def get_embedding(text: str, model: str = "text-embedding-3-small"):
    """Function to perform text embedding, see options from OpenAI's website at

    https://platform.openai.com/docs/guides/embeddings/embedding-models
    """
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding


def complete_text(prompt: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to generate output prompt for parent who are asking questions about newborn in Thai."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def get_response(question: str):
    question_embeddings = np.array([get_embedding(question)])
    D, I = index.search(question_embeddings, k=2)
    retrieved_chunk = [chunks[i] for i in I.tolist()[0]]
    
    prompt_with_context = f"""
    Context information is below.
    ---------------------
    {retrieved_chunk}
    ---------------------
    Given the context information and not prior knowledge, answer the given query in Thai. The answer should be concise and clear.
    Query: {question}
    Answer:
    """
    
    output_rag = complete_text(prompt_with_context)
    return output_rag



### Streamlit app

st.set_page_config(page_title="Chatbot", page_icon="", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title('Chat Interface')

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "สอบถามข้อมูลเกี่ยวกับการดูแลและพัฒนาเด็กเล็กวัย 0-3 ปีได้เลยครับ"}
    ]

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
messages = getattr(st.session_state, 'messages', [])
for message in messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

#If last message is not from assistant, generate a new response
if messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_response(prompt)
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message) # Add response to message history
