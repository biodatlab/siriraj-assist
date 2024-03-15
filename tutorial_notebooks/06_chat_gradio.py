import pickle
import json
import numpy as np
import gradio as gr
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


def generate_response(question: str, history: list = []):
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


gr.ChatInterface(generate_response, title="สอบถามข้อมูลเกี่ยวกับการดูแลและพัฒนาเด็กวัย 0-3 ปีได้เลยครับ").launch()