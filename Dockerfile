FROM python:3.8

# Install Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir unstructured chromadb tiktoken
RUN pip install --no-cache-dir langchain openai
RUN pip install --no-cache-dir jupyterlab jupyterlab-lsp python-lsp-server

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 5000

# Run Jupyter
CMD ["python", "qa.py"]
