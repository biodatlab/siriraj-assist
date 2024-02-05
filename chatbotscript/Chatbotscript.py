import openai
import streamlit as st
from llama_index import (
    KeywordTableIndex,
    SimpleDirectoryReader,
    ServiceContext,
)
from llama_index import VectorStoreIndex,download_loader
from llama_index.output_parsers import LangchainOutputParser
from llama_index.llms import OpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from pathlib import Path
import json

openai.api_key = "..."
st.set_page_config(page_title="Chatbot for doctor appointment", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Chatbot for doctor appointment")
st.info("แชทบอทช่วยตอบคำถามสำหรับการนัดหมายแพทย์ที่โรงพยาบาลศิริราช ปิยมหาราชการุณย์ ดูข้อมูลแพทย์เพิ่มเติมได้ที่ (https://www.siphhospital.com/th/medical-services/find-doctor)", icon="📃")
prompt = """
Given the following doctors' data in this format, craft a response in Thai to a patient asking about scheduling an appointment, inquiring about the doctor's expertise, or seeking a recommendation for a doctor based on their needs:

{
  "name": "...",
  "image_src": "...",
  "url": "...",
  "table_check": "...",
  "qualification": "...",
  "expertise": "..."
}

Use only the data provided in the JSONL file in the index. The response should be in Thai and tailored to the specific inquiry, whether it's about scheduling an appointment, the doctor's expertise, or a suggestion for a doctor based on the patient's condition or needs."""


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        file_path = "D:\BME\siriraj_doctor_details.jsonl"
        JSONReader = download_loader("JSONReader")
        loader = JSONReader()
        docs = loader.load_data(Path(file_path), is_jsonl=True)
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.3, system_prompt= prompt ))
        index = VectorStoreIndex.from_documents(docs,service_context=service_context)

        return index

index = load_data()

retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
)

# configure response synthesizer
response_synthesizer = get_response_synthesizer()

# assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.5)],
)
chat_engine = CondenseQuestionChatEngine.from_defaults(
    query_engine=query_engine,
    verbose=True,
)

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "สอบถามข้อมูลการนัดหมายแพทย์ได้ที่นี่ครับ"}
    ]

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = chat_engine

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
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
