FROM python:3.8

# Install Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir telegram python-telegram-bot
RUN pip install --no-cache-dir unstructured chromadb tiktoken
RUN pip install --no-cache-dir langchain openai

# Set working directory
WORKDIR /app

# labor law files
COPY files/cut/labor_standard_act_zhtw.txt files/cut/labor_standard_act_zhtw.txt
COPY files/cut/labor_pension_act_zhtw.txt files/cut/labor_pension_act_zhtw.txt

# chrome persist data
COPY lsa-data lsa-data
COPY lpa-data lpa-data
COPY chroma_logs.log chroma_logs.log

COPY lsa_ai_bot.py lsa_ai_bot.py
COPY lpa_ai_bot.py lpa_ai_bot.py

ARG OPENAI_API_KEY
ARG TELEGRAM_TOKEN

CMD ["python", "-u", "lsa_ai_bot.py"]
