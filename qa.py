#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
import os
os.environ['OPENAI_API_KEY'] = '...'
os.environ['TELEGRAM_TOKEN'] = '...'

import telegram
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.chains import RetrievalQA

def init_tg_bot():
    try:
        application = ApplicationBuilder().token(os.environ['TELEGRAM_TOKEN']).build()
        start_handler = CommandHandler('start', start)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
        application.add_handler(start_handler)
        application.add_handler(echo_handler)
        application.run_polling()
    except Exception as e:
        print(e)

def setup_chatgpt():
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
    docsearch = Chroma(embedding_function=embeddings, persist_directory="./chroma-data")
    return docsearch

def setup_qa_model(docsearch):
    qa = RetrievalQA.from_llm(llm=OpenAI(), retriever=docsearch.as_retriever())
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
    a=qa.run(q.content + ' Please provide the relevant legal provisions and the name of the law. Please provide a brief and straightforward answer, avoiding the use of double negatives.')
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

async def start(update, context):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="此機器人僅供問答而非聊天，因此不能連續發問，每個問題都是獨立的。目前僅載入勞動基準法，你可以嘗試提問：「我老闆沒通知就解僱我，這合法嗎？」")
    except Exception as e:
        print(e)

async def echo(update, context):
    try:
        human_message=human_message_prompt.format_messages(text=update.message.text)
        q = ask_chatbot(human_message, chat)
        a = get_answer(q, qa)
        output = translate_answer_to_chinese(a, chat, human_message_prompt_2)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=output)
    except Exception as e:
        print(e)

chat = setup_chatgpt()
docs = load_data()
texts = split_documents(docs)
embeddings = setup_embeddings()
docsearch = setup_vector_search(texts, embeddings)
qa = setup_qa_model(docsearch)
human_message_prompt = setup_human_message_prompt()
human_message_prompt_2 = setup_human_message_prompt_2()
        
# Initialize Telegram bot
init_tg_bot()
