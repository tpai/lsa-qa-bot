FROM python:3.8

# Install Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir telegram python-telegram-bot
RUN pip install --no-cache-dir unstructured chromadb tiktoken
RUN pip install --no-cache-dir langchain openai

# Set working directory
WORKDIR /app

COPY chroma-data chroma-data
COPY chroma_logs.log chroma_logs.log
COPY files/cut/labor_standard_act_zhtw.txt files/cut/labor_standard_act_zhtw.txt
COPY qa.py qa.py

ARG OPENAI_API_KEY
ARG TELEGRAM_TOKEN

# Run Jupyter
CMD ["python", "-u", "qa.py"]
