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
from langchain.text_splitter import TokenTextSplitter
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain.chains import RetrievalQA

def setup_chatgpt():
    chat=ChatOpenAI(model_name="gpt-3.5-turbo",temperature=0)
    return chat

def load_file():
    loader = UnstructuredFileLoader('./files/cut/labor_standard_act_zhtw.txt')
    # loader = DirectoryLoader('./files/cut/', glob='**/*.txt')
    docs = loader.load()
    print('file loaded')
    return docs

def split_documents(docs):
    text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)
    return texts

def setup_embeddings():
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])
    return embeddings

def setup_vector_search(texts, embeddings):
    docsearch = Chroma(embedding_function=embeddings, persist_directory="./chroma-data")
    # docsearch = Chroma.from_documents(texts, embeddings, persist_directory="./chroma-data")
    docsearch.persist()
    return docsearch

def setup_qa_model(docsearch):
    qa = RetrievalQA.from_llm(llm=OpenAI(), retriever=docsearch.as_retriever())
    return qa

def get_answer(q, qa, prefix='', suffix=''):
    q_map = {'勞基法': '勞動基準法', '老闆': '雇主', '員工': '勞工', '薪水': '工資', '工時': '工作時間', '特休': '特別休假', '未成年': '童工', '工讀生': '技術生', '年終': '年度終了', '勞退': '勞工退休金', '懷孕': '妊娠'}
    for key, value in q_map.items():
        q = q.replace(key, value)
    q_fixed = f"{prefix}{q}{suffix}"
    print(f'q={q_fixed}')
    a = qa.run(q_fixed)
    print(f'a={a}')
    return a

async def start(update, context):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="此機器人僅供問答而非聊天，因此不能連續發問，每個問題都是獨立的。\n你可以嘗試問「老闆欠薪」或者試試附上法條的「/law 老闆欠薪」。")
    except Exception as e:
        print(e)

async def law(update, context):
    try:
        a = get_answer(update.message.text.split(' ', 1)[1], qa, '', ' 請簡單回答，並附上相關的法條（如：第X條第X項）和情事。')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=a)
    except Exception as e:
        if 'index out of range' in str(e):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="請輸入你想問的問題")
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text="不明錯誤")
        print(e)

async def echo(update, context):
    try:
        a = get_answer(update.message.text, qa, '', ' 請簡單回答。')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=a)
    except Exception as e:
        if 'reduce your prompt' in str(e):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="請精簡你的問題")
            return
        if 'exceeded your current quota' in str(e):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="API Quota 用完囉")
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text="不明錯誤")
        print(e)

def init_tg_bot():
    try:
        application = ApplicationBuilder().token(os.environ['TELEGRAM_TOKEN']).build()
        start_handler = CommandHandler('start', start)
        law_handler = CommandHandler('law', law)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
        application.add_handler(start_handler)
        application.add_handler(law_handler)
        application.add_handler(echo_handler)
        application.run_polling()
    except Exception as e:
        print(e)
        
chat = setup_chatgpt()
docs = load_file()
texts = split_documents(docs)
embeddings = setup_embeddings()
docsearch = setup_vector_search(texts, embeddings)
qa = setup_qa_model(docsearch)

# Initialize Telegram bot
init_tg_bot()
