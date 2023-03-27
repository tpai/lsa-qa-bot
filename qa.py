#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, VectorDBQA, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.prompts.chat import HumanMessagePromptTemplate
from flask import Flask, request, jsonify
import os
# os.environ['OPENAI_API_KEY'] = '...'

app = Flask(__name__)

def setup_chatbot():
    chat=ChatOpenAI(model_name="gpt-3.5-turbo",temperature=0)
    return chat

def load_data():
    loader = UnstructuredFileLoader('./data/labor_standard_act.txt')
    docs = loader.load()
    print('data loaded')
    return docs

def split_documents(docs):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)
    return texts

def setup_embeddings():
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])
    return embeddings

def setup_vector_search(texts, embeddings):
    docsearch = Chroma.from_documents(texts, embeddings, persist_directory="./chroma-data")
    return docsearch

def setup_qa_model(docsearch):
    qa = VectorDBQA.from_chain_type(llm=OpenAI(), chain_type="stuff", vectorstore=docsearch)
    return qa

def setup_human_message_prompt():
    human_message_prompt=HumanMessagePromptTemplate(prompt=PromptTemplate(
        template="Translate the following input to English: {text}",
        input_variables=["text"],
    ))
    return human_message_prompt

def ask_chatbot(human_message, chat):
    q=chat(human_message)
    print('q=' + q.content)
    return q

def get_answer(q, qa):
    a=qa.run(q.content)
    print('a=' + a)
    return a

def setup_human_message_prompt_2():
    human_message_prompt=HumanMessagePromptTemplate(prompt=PromptTemplate(
        template="Translate the following input to Traditional Chinese: {text}",
        input_variables=["text"],
    ))
    return human_message_prompt

def translate_answer_to_chinese(a, chat, human_message_prompt):
    human_message=human_message_prompt.format_messages(text=a)
    output=chat(human_message)
    return output.content

chat = setup_chatbot()
docs = load_data()
texts = split_documents(docs)
embeddings = setup_embeddings()
docsearch = setup_vector_search(texts, embeddings)
qa = setup_qa_model(docsearch)
human_message_prompt = setup_human_message_prompt()
human_message_prompt_2 = setup_human_message_prompt_2()

@app.route('/ask', methods=['POST'])
def ask_api():
    human_message=human_message_prompt.format_messages(text=request.json['input'])
    q = ask_chatbot(human_message, chat)
    a = get_answer(q, qa)
    output = translate_answer_to_chinese(a, chat, human_message_prompt_2)
    response = jsonify({'response': output})
    response.headers.add('Access-Control-Allow-Origin', os.environ['HOSTNAME'])
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    return response

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
