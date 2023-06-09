#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
import os
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', '...')
TELEGRAM_TOKEN=os.environ.get('TELEGRAM_TOKEN', '...')

# enable memory cache
import langchain
from langchain.cache import InMemoryCache
langchain.llm_cache = InMemoryCache()

import telegram
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA

def setup_chatgpt():
    chat=OpenAI(model_name="gpt-3.5-turbo",temperature=0)
    return chat

def load_file():
    with open('./files/cut/labor_standard_act_zhtw.txt') as f:
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
    docsearch = Chroma(embedding_function=embeddings, persist_directory="./lsa-data")
    # docsearch = Chroma.from_texts(texts, embeddings, metadatas=[{"source": f'lsa-{str(i)}'} for i in range(len(texts))], persist_directory="./lsa-data")
    docsearch.persist()
    return docsearch

def setup_qa_model(llm, docsearch):
    qa = RetrievalQA.from_llm(llm=llm, retriever=docsearch.as_retriever(search_kwargs={"k": 2}))
    return qa

def get_answer(q, qa, prefix='', suffix=''):
    q_map = {'勞基法': '勞動基準法', '老闆': '雇主', '員工': '勞工', '薪水': '工資', '工時': '工作時間', '特休': '特別休假', '未成年': '童工', '工讀生': '技術生', '年終': '年度終了', '勞退': '勞工退休金', '懷孕': '妊娠', '曠職': '曠工'}
    for key, value in q_map.items():
        q = q.replace(key, value)
    q_fixed = f"{prefix}{q}{suffix}"
    print(f'q={q_fixed}')
    a = qa({"query":q_fixed})
    print(f'a={a["result"]}')
    return a["result"]

async def start(update, context):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="此機器人僅供問答而非聊天，因此不能連續發問，每個問題都是獨立的。\n你可以嘗試詢問「老闆欠薪」或「特休怎麼算」。")
    except Exception as e:
        print(e)

async def law(update, context):
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="TYPING")
        a = get_answer(update.message.text, qa, '', ' 請簡單說明條文')
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
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="TYPING")
            a = get_answer(prompt, qa, '', ' 請簡單說明條文')
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
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        start_handler = CommandHandler('start', start)
        law_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), law)
        yearendbonus_handler = CommandHandler('yearendbonus', predefined_handler('公司 盈餘 獎金 法條'))
        annualleave_handler = CommandHandler('annualleave', predefined_handler('特別休假 法條'))
        layoffwarning_handler = CommandHandler('layoffwarning', predefined_handler('不定期契約 終止勞動 預告期 法條'))
        severancepay_handler = CommandHandler('severancepay', predefined_handler('資遣費怎麼算'))
        retirement_handler = CommandHandler('retirement', predefined_handler('工作多久可以退休 法條'))
        maxovertime_handler = CommandHandler('maxovertime', predefined_handler('延長工時不能超過多久 法條'))
        overtimepay_handler = CommandHandler('overtimepay', predefined_handler('加班加給怎麼算'))
        workabsent_handler = CommandHandler('workabsent', predefined_handler('曠職 法條'))
        companybroke_handler = CommandHandler('companybroke', predefined_handler('公司破產 積欠工資 法條'))
        application.add_handler(start_handler)
        application.add_handler(law_handler)
        application.add_handlers([
            layoffwarning_handler, yearendbonus_handler, annualleave_handler,
            severancepay_handler, retirement_handler, maxovertime_handler,
            overtimepay_handler, workabsent_handler, companybroke_handler
        ])
        application.run_polling()
    except Exception as e:
        print(e)
        
chat = setup_chatgpt()
llm = setup_chatgpt()
file = load_file()
texts = split_texts(file)
embeddings = setup_embeddings()
docsearch = setup_vector_search(texts, embeddings)
qa = setup_qa_model(llm, docsearch)

# Initialize Telegram bot
init_tg_bot()
