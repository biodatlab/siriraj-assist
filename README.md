# Siriraj Assistant

A demo chatbot for finding suitable, scheduling, or ask for suggestions for medical doctor checkouts at Siriraj.
The chatbot should make a conversation in Thai and perform suggestions based on doctor's schedule and expertise
based on user's requests.

We scrape the dataset from SIP hospital and make an example Thai chatbot with ChatGPT and Vertex AI using RAG pipeline. We run the application
using Streamlit or Gradio. The main purpose is to give an example how to use retrieval augmented generation using RAG pipeline and discuss some potential solutions at the Mahidol Hackathon Event (happened on March 16-24, 2024).

## Project structure

- `scipts`: Contains the scraping script to download doctor's data to CSV file
- `chatbotscript`: Contains an example script implemeting RAG pipeline on the CSV data (not working well yet! that's why you're here at the hackathon)
- `data`: Contains scraped dataset in CSV format and example 
- `tutorial_notebooks`: contains scripts for prompting with ChatGPT or VertexAI, RAG pipeline with a given example (book), and script for running an application using Gradio and Streamlit.

## Requirements

See `requirements.txt` for some dependencies. However, you should refer to API keys according to platform you use (ChatGPT, VertextAI, MistralAI, etc.).