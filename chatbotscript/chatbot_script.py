import streamlit as st
import openai
from llama_index import (
    KeywordTableIndex,
    ServiceContext,
)
from llama_index import VectorStoreIndex,download_loader
from pathlib import Path
from llama_index.retrievers import VectorIndexRetriever
from llama_index.llms import OpenAI



openai.api_key = "...."
st.set_page_config(page_title="Chatbot for doctor appointment", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Chatbot for doctor appointment")
st.info("แชทบอทช่วยตอบคำถามสำหรับการนัดหมายแพทย์ที่โรงพยาบาลศิริราช ปิยมหาราชการุณย์ ดูข้อมูลแพทย์เพิ่มเติมได้ที่ (https://www.siphhospital.com/th/medical-services/find-doctor)", icon="📃")

system_prompt = """
Given the following doctors' data in the CSV file and embedded, create a response in Thai to a patient asking about scheduling an appointment, inquiring about the doctor's expertise, or seeking a recommendation for a doctor based on their needs. Use only the data provided. The response should be in Thai and do not hallucinate. If the patient wants to make an appointment, create a CSV file content for a list of doctor appointments. The CSV should include columns for Doctor's Name, Appointment Time, Appointment Date, and Expertise. Ensure that the appointment times and dates match with the database. Format the data to align with standard CSV formatting conventions, including headers and comma-separated values. Provide the content as plain text that can be copied into a CSV file and confirm with the patient.
"""

llm= OpenAI(model="gpt-4",system_prompt=system_prompt,temperature=0.3)
service_context = ServiceContext.from_defaults(llm=llm)
@st.cache_resource(show_spinner=False)

def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        file_path = "./data/siriraj_doctor_details(2).csv"
        PandasCSVReader = download_loader("PandasCSVReader")
        loader = PandasCSVReader()
        docs = loader.load_data(file=Path(file_path))
        index = VectorStoreIndex.from_documents(docs,service_context=service_context)
    return index

index = load_data()
chat_engine = index.as_chat_engine(chat_mode="context")

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

