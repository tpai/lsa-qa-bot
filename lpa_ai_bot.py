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
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA

def setup_chatgpt():
    chat=ChatOpenAI(model_name="gpt-4",temperature=0)
    return chat

def load_file():
    with open('./files/cut/labor_pension_act_zhtw.txt') as f:
        file = f.read()
    print('file loaded')
    return file

def split_texts(file):
    text_splitter = CharacterTextSplitter(chunk_size=500,chunk_overlap=0)
    texts = text_splitter.split_text(file)
    return texts

def setup_embeddings():
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])
    return embeddings

def setup_vector_search(texts, embeddings):
    docsearch = Chroma(embedding_function=embeddings, persist_directory="./lpa-data")
    # docsearch = Chroma.from_texts(texts, embeddings, metadatas=[{"source": f'lpa-{str(i)}'} for i in range(len(texts))], persist_directory="./lpa-data")
    docsearch.persist()
    return docsearch

def setup_qa_model(docsearch):
    qa = RetrievalQA.from_llm(llm=OpenAI(), retriever=docsearch.as_retriever(search_kwargs={"k": 2}))
    return qa

def get_answer(q, qa, prefix='', suffix=''):
    q_map = {'勞基法': '勞動基準法', '老闆': '雇主', '員工': '勞工', '薪水': '工資', '年終': '年度終了', '勞退': '勞工退休金'}
    for key, value in q_map.items():
        q = q.replace(key, value)
    q_fixed = f"{prefix}{q}{suffix}"
    print(f'q={q_fixed}')
    a = qa({"query":q_fixed})
    print(f'a={a["result"]}')
    return a["result"]

async def start(update, context):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="此機器人僅供問答而非聊天，因此不能連續發問，每個問題都是獨立的。\n你可以嘗試詢問「退休金領取方式有幾種？」。")
    except Exception as e:
        print(e)

async def law(update, context):
    try:
        a = get_answer(update.message.text, qa, '', ' 請簡單回答')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=a)
    except Exception as e:
        print(e)
        if 'index out of range' in str(e):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="請輸入你想問的問題")
            return
        if 'reduce your prompt' in str(e):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="請精簡你的問題")
            return
        if 'exceeded your current quota' in str(e):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="API Quota 用完囉")
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text="不明錯誤")

def predefined_handler(prompt):
    async def predefined(update, context):
        try:
            a = get_answer(prompt, qa, '', ' 請簡單回答')
            await context.bot.send_message(chat_id=update.effective_chat.id, text=a)
        except Exception as e:
            print(e)
            if 'index out of range' in str(e):
                await context.bot.send_message(chat_id=update.effective_chat.id, text="請輸入你想問的問題")
                return
            if 'reduce your prompt' in str(e):
                await context.bot.send_message(chat_id=update.effective_chat.id, text="請精簡你的問題")
                return
            if 'exceeded your current quota' in str(e):
                await context.bot.send_message(chat_id=update.effective_chat.id, text="API Quota 用完囉")
                return
            await context.bot.send_message(chat_id=update.effective_chat.id, text="不明錯誤")
    return predefined

def init_tg_bot():
    try:
        application = ApplicationBuilder().token(os.environ['TELEGRAM_TOKEN']).build()
        start_handler = CommandHandler('start', start)
        law_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), law)
        retirepayment_handler = CommandHandler('retirepayment', predefined_handler('退休金領取方式的法條'))
        pensionportion_handler = CommandHandler('pensionportion', predefined_handler('老闆應提繳多少比例之退休金 法條'))
        application.add_handler(start_handler)
        application.add_handler(law_handler)
        application.add_handlers([
            retirepayment_handler, pensionportion_handler
        ])
        application.run_polling()
    except Exception as e:
        print(e)
        
chat = setup_chatgpt()
file = load_file()
texts = split_texts(file)
embeddings = setup_embeddings()
docsearch = setup_vector_search(texts, embeddings)
qa = setup_qa_model(docsearch)

# Initialize Telegram bot
init_tg_bot()
